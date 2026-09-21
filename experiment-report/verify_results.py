"""Extract report evidence directly from Gaussian logs; no spectral refitting."""
from pathlib import Path
import csv
import hashlib
import json
import re
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SCALE = 0.9613
HARTREE_KJ_MOL = 2625.49962


def parse(folder):
    path = ROOT / folder / 'job.out'
    text = path.read_text()
    assert 'Normal termination' in text.splitlines()[-1]
    n = int(re.findall(r'NAtoms=\s*(\d+)', text)[-1])
    arrays = {}
    for key, prefix in [('frequency', 'Frequencies'), ('ir', 'IR Inten'), ('raman', 'Raman Activ')]:
        arrays[key] = np.array([float(x) for line in re.findall(prefix + r'\s*--([^\n]+)', text) for x in line.split()])
        assert len(arrays[key]) == 3*n-6
    assert np.all(arrays['frequency'] > 0)
    patterns = {
        'E': r'SCF Done:\s+E\(RB3LYP\)\s*=\s*([-\d.]+)',
        'Z': r'Sum of electronic and zero-point Energies=\s*([-\d.]+)',
        'H': r'Sum of electronic and thermal Enthalpies=\s*([-\d.]+)',
        'G': r'Sum of electronic and thermal Free Energies=\s*([-\d.]+)',
    }
    result = {key: float(re.findall(pattern, text)[-1]) for key, pattern in patterns.items()}
    result.update(source=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  atoms=n, modes=len(arrays['frequency']), min=float(min(arrays['frequency'])),
                  negative_modes=int(sum(arrays['frequency'] < 0)),
                  temperature_K=298.15, pressure_atm=1.0,
                  grid=re.findall(r'IXCGrd=.*', text)[-1].strip())
    assert re.search(r'Temperature\s+298.150 Kelvin.\s+Pressure\s+1.00000 Atm.', text)
    orientation = text.rsplit('Standard orientation:', 1)[1].splitlines()
    atom_rows = [line.split() for line in orientation[5:5+n]]
    assert len(atom_rows) == n and all(len(row) == 6 for row in atom_rows)
    xyz = np.array([[float(x) for x in row[3:]] for row in atom_rows])
    atomic_numbers = np.array([int(row[1]) for row in atom_rows])
    displacement = []
    for block in text.split('Frequencies --')[1:]:
        lines = block.split('  Atom  AN', 1)[1].splitlines()[1:1+n]
        numbers = np.array([[float(x) for x in line.split()[2:]] for line in lines])
        assert numbers.shape == (n, 9)
        displacement.extend(numbers.reshape(n, 3, 3).transpose(1, 0, 2))
    return result, arrays, xyz, atomic_numbers, np.array(displacement)


parsed = [parse(folder) for folder in ['Raman-chk1', 'Raman-chk2', 'double']]
a, b, d = [p[0] for p in parsed]
keys = ['E', 'Z', 'H', 'G']
result = {
    'conformers': [a, b], 'dimer': d,
    'delta_2_minus_1_kJ_mol': {k: (b[k]-a[k])*HARTREE_KJ_MOL for k in keys},
    'dimer_minus_2_conformer1_kJ_mol': {k: (d[k]-2*a[k])*HARTREE_KJ_MOL for k in keys},
    'association_caveats': 'Per mole of dimers formed from two conformer-1 monomers; no BSSE correction, gas-phase harmonic 298.15 K/1 atm; no crystal or solution free energy.',
    'frequency_scale': SCALE,
}
_, arrays, xyz, atomic_numbers, displacement = parsed[-1]
bond_pairs = {'C8_O13': (8,13), 'C18_O16': (18,16), 'O15_H14': (15,14), 'O19_H20': (19,20)}
result['dimer_bond_lengths_A'] = {name: float(np.linalg.norm(xyz[i-1]-xyz[j-1])) for name,(i,j) in bond_pairs.items()}
contacts = []
for donor, hydrogen, acceptor in [(15,14,16), (19,20,13)]:
    assert atomic_numbers[donor-1] == atomic_numbers[acceptor-1] == 8
    assert atomic_numbers[hydrogen-1] == 1
    u, v = xyz[donor-1]-xyz[hydrogen-1], xyz[acceptor-1]-xyz[hydrogen-1]
    contacts.append(dict(donor=donor, hydrogen=hydrogen, acceptor=acceptor,
                         OH_A=float(np.linalg.norm(u)), HO_A=float(np.linalg.norm(v)),
                         OO_A=float(np.linalg.norm(xyz[donor-1]-xyz[acceptor-1])),
                         OHO_angle_deg=float(np.degrees(np.arccos(np.dot(u,v)/np.linalg.norm(u)/np.linalg.norm(v))))))
result['dimer_hydrogen_bond_geometry'] = contacts
result['dimer_selected_modes'] = []
for mode in [44, 56, 70, 71, 72, 73, 74, 76]:
    j = mode-1
    result['dimer_selected_modes'].append(dict(mode=mode, raw_cm_1=float(arrays['frequency'][j]),
        scaled_cm_1=float(arrays['frequency'][j]*SCALE), IR_km_mol=float(arrays['ir'][j]),
        Raman_activity=float(arrays['raman'][j])))
with (ROOT/'experiment-report/verified_results.json').open('w') as handle:
    json.dump(result, handle, indent=2, ensure_ascii=False)
    handle.write('\n')

# Linearized changes of selected bond lengths from the printed Cartesian
# normal-mode displacements (rounded by Gaussian). Signs reflect an arbitrary
# mode phase; these values are qualitative checks, not a PED or an intensity.
with (ROOT/'experiment-report/dimer_mode_bond_projections.csv').open('w', newline='') as handle:
    writer = csv.writer(handle)
    writer.writerow(['mode', 'scaled_cm-1', 'IR_km_mol-1', 'Raman_activity', *bond_pairs])
    for j, (freq, ir, raman) in enumerate(zip(arrays['frequency'], arrays['ir'], arrays['raman'])):
        projections = []
        for i, k in bond_pairs.values():
            unit = (xyz[k-1]-xyz[i-1])/np.linalg.norm(xyz[k-1]-xyz[i-1])
            projections.append(float(np.dot(displacement[j,k-1]-displacement[j,i-1], unit)))
        writer.writerow([j+1, freq*SCALE, ir, raman, *projections])
print(json.dumps(result, indent=2, ensure_ascii=False))

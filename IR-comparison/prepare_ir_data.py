"""Reproducible IR extraction, raster digitization and broadening."""
from pathlib import Path
from html.parser import HTMLParser
import csv
import argparse
import re
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent

class Tables(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows=[]; self.row=[]; self.cell=None
    def handle_starttag(self, tag, attrs):
        if tag=='tr': self.row=[]
        if tag in ('td','th'): self.cell=''
    def handle_data(self, data):
        if self.cell is not None: self.cell+=data
    def handle_endtag(self, tag):
        if tag in ('td','th') and self.cell is not None:
            self.row.append(self.cell.strip()); self.cell=None
        if tag=='tr': self.rows.append(self.row)

def save(name, header, rows):
    with (ROOT/name).open('w', newline='') as f:
        w=csv.writer(f); w.writerow(header); w.writerows(rows)

def gaussian(folder):
    text=(ROOT.parent/folder/'job.out').read_text()
    assert 'Normal termination' in text.splitlines()[-1]
    atoms=int(re.findall(r'NAtoms=\s*(\d+)',text)[-1])
    expected=3*atoms-6  # All molecules in this comparison are nonlinear.
    freq=np.array([float(x) for line in re.findall(r'Frequencies --([^\n]+)',text) for x in line.split()])
    inten=np.array([float(x) for line in re.findall(r'IR Inten\s+--([^\n]+)',text) for x in line.split()])
    assert len(freq)==len(inten)==expected and np.all(freq>0) and np.all(inten>=0)
    save(folder+'_ir_modes.csv',['mode','raw_cm-1','scaled_cm-1','IR_km_mol-1'],
         zip(range(1,expected+1),freq,freq*.9613,inten))
    print(f'{folder}: {atoms} atoms, {expected} positive modes; minimum {freq.min():.4f} cm-1')
    return freq*.9613,inten

cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument('--redigitize', action='store_true',
                 help='Re-extract from locally obtained SDBS GIF and NIST HTML in sources/')
args=cli.parse_args()
if args.redigitize:
    parser=Tables(); parser.feed((ROOT/'sources/nist_reference.html').read_text())
    rows=[]
    for row in parser.rows:
        if len(row)>=5 and row[0].isdigit() and row[1] in ("A'",'A"'):
            rows.append([int(row[0]),float(row[2]),float(row[3]),float(row[4])])
    rows=list({row[0]:row for row in rows}.values())
    rows.sort(key=lambda row:row[0])
    assert len(rows)==39, (len(rows),rows[:2])
    save('reference_ir_modes.csv',['mode','raw_cm-1','scaled_cm-1','IR_km_mol-1'],rows)
ref=np.loadtxt(ROOT/'reference_ir_modes.csv', delimiter=',', skiprows=1)
assert ref.shape==(39,4) and np.all(np.isfinite(ref))

# SDBS axes: 4000 (x=30), 2000 (x=293), 400 (x=714);
# transmittance 100% (y=97), 0% (y=418). Plot has a slope break at 2000.
if args.redigitize:
    im=np.asarray(Image.open(ROOT/'sources/SDBS_IR_NIDA63340.gif').convert('L'))
    xs=np.arange(31,714)
    ys=[]
    for x in xs:
        dark=np.flatnonzero(im[103:411,x]<128)+103
        ys.append(np.median(dark) if len(dark) else np.nan)
    ys=np.array(ys); good=np.isfinite(ys)
    assert good.mean()>.99
    ys=np.interp(xs,xs[good],ys[good])
    freq=np.where(xs<=293,4000-(xs-30)*2000/263,2000-(xs-293)*1600/421)
    T=(418-ys)/321
    A=-np.log10(T)
    save('experimental_ir_digitized.csv',['wavenumber_cm-1','transmittance_fraction','absorbance'],zip(freq,T,A))
experiment=np.loadtxt(ROOT/'experimental_ir_digitized.csv', delimiter=',', skiprows=1)
assert experiment.shape[1]==3 and np.all(np.isfinite(experiment))
freq,T,A=experiment.T
assert np.all(np.diff(freq)<0) and np.all((T>0)&(T<=1))
grid=np.arange(400.,4001.)
exp=np.interp(grid,freq[::-1],A[::-1],left=np.nan,right=np.nan)
exp-=np.nanmin(exp); exp/=np.nanmax(exp)
def broaden(f,i):
    s=20/(2*np.sqrt(2*np.log(2)))
    y=np.exp(-.5*((grid[:,None]-f)/s)**2)@i
    return y/y.max()
calc=[broaden(ref[:,2],ref[:,3])]
for folder in ['Raman-chk1','Raman-chk2','double']: calc.append(broaden(*gaussian(folder)))
save('ir_spectra_normalized.csv',['wavenumber_cm-1','experiment','reference','conformer1','conformer2','dimer'],zip(grid,exp,*calc))
print('Experimental raster coverage:',freq.min(),freq.max())

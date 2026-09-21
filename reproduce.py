"""Rebuild spectra and report evidence from the committed Gaussian outputs."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def run(command, cwd=ROOT):
    print('+', ' '.join(str(x) for x in command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-only', action='store_true', help='No R or XeLaTeX needed')
    parser.add_argument('--tex', action='store_true', help='Also compile the report twice')
    args = parser.parse_args()
    if not args.data_only and not shutil.which('Rscript'):
        parser.error('Rscript not found. See ENVIRONMENT.md or use --data-only.')
    if args.tex and not shutil.which('xelatex'):
        parser.error('xelatex not found. See ENVIRONMENT.md.')
    run([sys.executable, 'prepare_ir_data.py'], ROOT/'IR-comparison')
    run([sys.executable, 'prepare_raman_data.py', '--chk1', '../Raman-chk1/job.out',
         '--chk2', '../Raman-chk2/job.out', '--dimer', '../double/job.out',
         '--output-dir', '.'], ROOT/'Raman-comparison')
    run([sys.executable, 'experiment-report/verify_results.py'])
    if not args.data_only:
        for kind in ('ir', 'raman'):
            folder = ROOT / ('IR-comparison' if kind=='ir' else 'Raman-comparison')
            run(['Rscript', f'plot_{kind}_comparison.R',
                 f'{kind}_spectra_normalized.csv', f'{kind}_comparison'], folder)
    if args.tex:
        report = ROOT/'experiment-report'
        (report/'tex-build').mkdir(exist_ok=True)
        for _ in range(2):
            run(['xelatex', '-interaction=nonstopmode', '-halt-on-error',
                 '-output-directory=tex-build', 'benzoic_acid_ir_raman.tex'], report)
    print('Reproduction completed successfully.')


if __name__ == '__main__':
    main()

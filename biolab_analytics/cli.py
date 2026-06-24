
import argparse
from biolab_analytics.calculators.solution_chemistry import mass_for_molar_solution
from biolab_analytics.calculators.dilution import c1v1
from biolab_analytics.calculators.microbiology import cfu_per_ml
from biolab_analytics.calculators.sequencing import genome_coverage

def main():
    parser = argparse.ArgumentParser(description="BioLab Analytics CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    mol = sub.add_parser("molarity")
    mol.add_argument("--molarity", type=float, required=True)
    mol.add_argument("--volume-l", type=float, required=True)
    mol.add_argument("--mw", type=float, required=True)

    dil = sub.add_parser("dilution")
    dil.add_argument("--c1", type=float, required=True)
    dil.add_argument("--c2", type=float, required=True)
    dil.add_argument("--v2", type=float, required=True)

    cfu = sub.add_parser("cfu")
    cfu.add_argument("--colonies", type=float, required=True)
    cfu.add_argument("--dilution", type=float, required=True)
    cfu.add_argument("--volume-ml", type=float, required=True)

    cov = sub.add_parser("coverage")
    cov.add_argument("--reads", type=float, required=True)
    cov.add_argument("--read-length", type=float, required=True)
    cov.add_argument("--genome-size", type=float, required=True)

    args = parser.parse_args()

    if args.command == "molarity":
        print(f"Mass required: {mass_for_molar_solution(args.molarity, args.volume_l, args.mw):.6f} g")
    elif args.command == "dilution":
        stock, diluent = c1v1(args.c1, args.c2, args.v2)
        print(f"Stock volume: {stock:.6f}")
        print(f"Diluent volume: {diluent:.6f}")
    elif args.command == "cfu":
        print(f"CFU/mL: {cfu_per_ml(args.colonies, args.dilution, args.volume_ml):.3e}")
    elif args.command == "coverage":
        print(f"Coverage: {genome_coverage(args.reads, args.read_length, args.genome_size):.2f}x")

if __name__ == "__main__":
    main()

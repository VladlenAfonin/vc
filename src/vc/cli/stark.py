import argparse

from vc.cli.fri import FriOptionsDefault
from vc.cli.airs import fibonacci


def parse_arguments(
    subparsers: argparse._SubParsersAction,  # [argparse._ArgumentParserT],
) -> None:
    parser = subparsers.add_parser(
        "stark",
        description="subprogram for running STARK with specified parameters for proving the results of a specified task",
        help="run STARK for one of preprogrammed tasks",
    )
    parser.set_defaults(func=main)

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        dest="list",
        help="list available AIRs for experimanting with",
        default=False,
        required=False,
    )

    parser.add_argument(
        "-a",
        "--air",
        action="store",
        dest="air",
        help="chose the function STARK should prove the result for. default: fibonacci",
        type=str,
        default="fibonacci",
        choices=["fibonacci", "factorial", "count"],
    )

    parser.add_argument(
        "--ff",
        "--folding-factor-log",
        action="store",
        dest="folding_factor_log",
        help=f"folding factor. default: {FriOptionsDefault.folding_factor_log_default}",
        nargs=1,
        default=[FriOptionsDefault.folding_factor_log_default],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    parser.add_argument(
        "--ef",
        "--expansion-factor-log",
        action="store",
        dest="expansion_factor_log",
        help=f"expansion factor. default: {FriOptionsDefault.expansion_factor_log_default}",
        nargs=1,
        default=[FriOptionsDefault.expansion_factor_log_default],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    parser.add_argument(
        "--fd",
        "--final-degree-log",
        action="store",
        dest="final_degree_log",
        help=f"number of coefficients when to stop the protocol. default: {FriOptionsDefault.final_degree_log_default}",
        nargs=1,
        default=[FriOptionsDefault.final_degree_log_default],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    parser.add_argument(
        "--sl",
        "--security-level-bits",
        action="store",
        dest="security_level_bits",
        help=f"desired security level in bits. default: {FriOptionsDefault.security_level_bits_default}",
        nargs=1,
        default=[FriOptionsDefault.security_level_bits_default],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    parser.add_argument(
        "-s",
        "--seed",
        action="store",
        dest="seed",
        help=f"randomness seed. default: 64 bit integer chosen at random",
        nargs=1,
        default=[None],
        required=False,
        metavar="NUMBER",
        type=int,
    )

    parser.add_argument(
        "air_arguments",
        nargs="*",
        help='arguments to pass to AIR generation, like "n" in fibonacci(n)',
        default=[None],
    )


def main(args: argparse.Namespace) -> int:
    if args.air == "fibonacci":
        return fibonacci.run(args)

    print("not implemented yet")
    return 0

import argparse


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
        "--air",
        action="store",
        dest="air",
        help="chose the function STARK should prove the result for",
        type=str,
        default="fibonacci",
        choices=["fibonacci", "factorial", "count"],
    )


def main(args: argparse.Namespace) -> int:
    print(args)
    return 0

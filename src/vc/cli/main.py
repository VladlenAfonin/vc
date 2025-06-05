import logging
import logging.config
import sys
import argparse

import vc.cli.fri
import vc.cli.stark


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s:%(name)s:%(funcName)s():%(message)s",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        # "vc.cli.main": {"level": "INFO", "handlers": ["stdout"]},
        # "vc.fri.prover": {"level": "DEBUG", "handlers": ["stdout"]},
        # "vc.fri.verifier": {"level": "DEBUG", "handlers": ["stdout"]},
    },
}

logger = logging.getLogger(__name__)
logging.config.dictConfig(logging_config)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="vc",
        description="verifiable computations (VC) experimentation program",
    )

    subparsers = parser.add_subparsers(
        required=True,
        title="subprograms",
        description="choose one of the subprograms for running and experimenting with corresponding protocols or primitives",
    )

    vc.cli.fri.parse_arguments(subparsers)
    vc.cli.stark.parse_arguments(subparsers)

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

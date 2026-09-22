"""Entry point for the `anonymize` command."""

import sys

from anonymizer.core import __version__


def main(argv: list[str] | None = None) -> int:
    """Run the command-line client.

    Args:
        argv: Argument list to parse. Defaults to `sys.argv[1:]`.

    Returns:
        Process exit code.
    """
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] in {"-V", "--version"}:
        print(__version__)
        return 0
    print("anonymizer: pipeline not implemented yet", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

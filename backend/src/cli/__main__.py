"""CLI entry point for documentation-service management commands."""

import argparse
import asyncio
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m src.cli",
        description="Documentation Service CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # seed command
    seed_parser = subparsers.add_parser("seed", help="Seed database with sample data")
    seed_parser.add_argument(
        "--fixture",
        choices=["demo", "minimal"],
        default="demo",
        help="Fixture set to load (default: demo)",
    )
    seed_parser.add_argument(
        "--force",
        action="store_true",
        help="Drop existing seed data and reseed",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "seed":
        from src.cli.seed import seed_database
        asyncio.run(seed_database(fixture=args.fixture, force=args.force))


if __name__ == "__main__":
    main()

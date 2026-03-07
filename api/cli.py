import argparse
import asyncio
import os
import sys


DEFAULT_API_URL = "http://127.0.0.1:8000/graphql"


async def list_employees(api_url: str) -> int:
    try:
        from generated_client.client import Client
    except ModuleNotFoundError:
        print("generated_client is missing. Run `make codegen` first.", file=sys.stderr)
        return 2

    client = Client(url=api_url)

    try:
        result = await client.get_employees()
    except Exception as exc:
        print(f"Failed to fetch employees: {exc}", file=sys.stderr)
        return 1

    print(result.model_dump_json(indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Employee API CLI")
    parser.add_argument(
        "--url",
        default=os.getenv("API_URL", DEFAULT_API_URL),
        help="GraphQL endpoint URL (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List all employees")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list":
        return asyncio.run(list_employees(args.url))

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

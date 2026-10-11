import argparse
import asyncio
import sys

from omniload.core import LoadGenerator, print_summary


def parse_args():
    parser = argparse.ArgumentParser(
        description="A concurrent HTTP load generator that mitigates coordinated omission."
    )
    parser.add_argument(
        "url",
        type=str,
        help="Target URL to load test (e.g., http://localhost:8080/)"
    )
    parser.add_argument(
        "--qps",
        type=float,
        required=True,
        help="Target Queries Per Second"
    )
    parser.add_argument(
        "--duration",
        type=float,
        required=True,
        help="Test duration in seconds"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    if args.qps <= 0:
        print("Error: QPS must be greater than 0", file=sys.stderr)
        sys.exit(1)
        
    if args.duration <= 0:
        print("Error: Duration must be greater than 0", file=sys.stderr)
        sys.exit(1)

    print(f"Starting load test on {args.url}")
    print(f"Target QPS: {args.qps}, Duration: {args.duration}s")
    
    try:
        generator = LoadGenerator(url=args.url, qps=args.qps, duration=args.duration)
        results = asyncio.run(generator.run())
        print_summary(results)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()

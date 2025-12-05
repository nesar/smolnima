#!/usr/bin/env python3
"""Command-line interface for smolnima."""

import sys
import argparse
from typing import Optional

from .config import Config
from .agent import create_nima_agent


def run_interactive(config: Config):
    """Run interactive chat session."""
    print("=" * 60)
    print("Dr. NIMA - Nuclear Imaging with Multi-Agents")
    print("Powered by smolagents")
    print("=" * 60)
    print("\nType 'exit' or 'quit' to end the session")
    print("Type 'help' for example questions\n")

    # Create agent
    agent = create_nima_agent(config)

    # Interactive loop
    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break

            if user_input.lower() == "help":
                print_help()
                continue

            # Run agent
            print("\nDr. NIMA: ", end="", flush=True)
            result = agent.run(user_input)
            print(result)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            if config.verbose:
                import traceback
                traceback.print_exc()


def run_single_query(query: str, config: Config):
    """Run a single query and exit."""
    agent = create_nima_agent(config)
    result = agent.run(query)
    print(result)


def print_help():
    """Print example questions."""
    examples = [
        "How are GPDs, QCFs and CFFs related to each other?",
        "Calculate the relativistic energy of an electron with momentum 100 MeV/c",
        "What is the Lorentz factor for a particle moving at 0.9c?",
        "Generate 10000 physics events and show me the statistics",
        "Visualize quark distributions",
        "What are the properties of a muon?",
    ]

    print("\nExample questions:")
    for i, ex in enumerate(examples, 1):
        print(f"  {i}. {ex}")


def main(argv: Optional[list] = None):
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Dr. NIMA - Nuclear Imaging with Multi-Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python -m smolnima.cli

  # Single query
  python -m smolnima.cli -q "What is the mass of a proton?"

  # Specify API key
  python -m smolnima.cli --api-key YOUR_KEY

  # Use different model
  python -m smolnima.cli --model gemini-2.5-pro
        """
    )

    parser.add_argument(
        "-q", "--query",
        help="Run single query and exit"
    )
    parser.add_argument(
        "--api-key",
        help="Google API key (or set GOOGLE_API_KEY env var)"
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini model to use (default: gemini-2.5-flash)"
    )
    parser.add_argument(
        "--pdfs-dir",
        default="./pdfs",
        help="Directory containing PDF documents (default: ./pdfs)"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=10,
        help="Maximum agent steps (default: 10)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Model temperature (default: 0.3)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args(argv)

    # Create config
    config = Config(
        api_key=args.api_key,
        model_name=args.model,
        pdfs_dir=args.pdfs_dir,
        max_steps=args.max_steps,
        temperature=args.temperature,
        verbose=args.verbose
    )

    # Check API key
    if not config.api_key:
        print("Error: Google API key not provided.", file=sys.stderr)
        print("Set GOOGLE_API_KEY environment variable or use --api-key", file=sys.stderr)
        return 1

    # Run mode
    if args.query:
        run_single_query(args.query, config)
    else:
        run_interactive(config)

    return 0


if __name__ == "__main__":
    sys.exit(main())

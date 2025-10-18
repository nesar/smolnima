#!/usr/bin/env python3
"""Example usage of smolnima."""

import os
from smolnima import create_nima_agent, Config


def main():
    """Run example queries."""

    # Ensure API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("Please set GOOGLE_API_KEY environment variable")
        return

    # Create config
    config = Config.from_env()
    config.verbose = True

    print("Creating Dr. NIMA agent...")
    agent = create_nima_agent(config)

    # Example queries
    examples = [
        "What is the mass of a proton in MeV?",
        "Calculate the Lorentz factor for a particle moving at 0.9c",
        "What is the decay probability of a muon after 1 microsecond?",
    ]

    for i, query in enumerate(examples, 1):
        print(f"\n{'='*60}")
        print(f"Example {i}: {query}")
        print('='*60)

        try:
            result = agent.run(query)
            print(f"\nResult:\n{result}")
        except Exception as e:
            print(f"Error: {e}")

    print(f"\n{'='*60}")
    print("Examples completed!")
    print('='*60)


if __name__ == "__main__":
    main()

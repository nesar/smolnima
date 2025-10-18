"""Allow running smolnima as a module: python -m smolnima"""

from .cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())

import sys

from balatro_env.data.cli import main

if __name__ == "__main__":  # multiprocessing spawn re-imports this module as __mp_main__ (dataops headless workers)
    sys.exit(main())

#!/usr/bin/env python
"""Simple entry point for running the bot."""
import sys
import os

# Add src to path for direct execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bot import main

if __name__ == "__main__":
    main()

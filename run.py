#!/usr/bin/env python
"""Simple entry point for running the bot.

Usage:
    python run.py              # Run once and exit (default - for cron/testing)
    python run.py --continuous # Run continuously (scans every 15 minutes)
"""
import sys
import os

# Add src to path for direct execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bot import main

if __name__ == "__main__":
    main()

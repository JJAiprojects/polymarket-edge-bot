#!/bin/bash
# Startup script for Render deployment
# This ensures the bot runs correctly on Render

# Create necessary directories
mkdir -p data logs

# Run the bot
python -m src.bot --once

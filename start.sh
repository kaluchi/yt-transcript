#!/bin/bash
# Quick start script for YouTube Transcript Bot

set -e

echo "=========================================="
echo "YouTube Transcript Bot - Quick Start"
echo "=========================================="
echo ""

# Check if environment variables are set
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$YOUTUBE_API_KEY" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Required environment variables not set!"
    echo ""
    echo "Please export the following variables:"
    echo "   export TELEGRAM_BOT_TOKEN=your_token"
    echo "   export YOUTUBE_API_KEY=your_key"
    echo "   export OPENAI_API_KEY=your_key"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Verify configuration
echo ""
echo "🔍 Verifying configuration..."
python scripts/check_config.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All checks passed!"
    echo ""
    echo "🚀 Starting bot..."
    echo ""
    python -m src.bot
else
    echo ""
    echo "❌ Configuration check failed!"
    echo "Please fix the errors above and try again."
    exit 1
fi

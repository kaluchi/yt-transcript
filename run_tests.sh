#!/bin/bash
# Run tests with coverage report

set -e

echo "=========================================="
echo "Running YouTube Transcript Bot Tests"
echo "=========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "🧪 Running tests..."
echo ""

# Run tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Tests completed!"
echo ""
echo "📊 Coverage report generated in htmlcov/index.html"
echo "   Open it in your browser to view detailed coverage."

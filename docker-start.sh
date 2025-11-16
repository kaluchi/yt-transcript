#!/bin/bash
# Docker deployment script for YouTube Transcript Bot

set -e

echo "=========================================="
echo "YouTube Transcript Bot - Docker Deployment"
echo "=========================================="
echo ""

# Function to check if environment variable is set
check_env() {
    local var_name=$1
    if [ -z "${!var_name}" ]; then
        echo "❌ Error: $var_name is not set"
        return 1
    else
        echo "✓ $var_name is set"
        return 0
    fi
}

echo "🔍 Checking required environment variables..."
echo ""

# Check all required variables
all_set=true

if ! check_env "YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN"; then
    all_set=false
fi

if ! check_env "YT_TRANSCRIPT_YOUTUBE_API_KEY"; then
    all_set=false
fi

if ! check_env "YT_TRANSCRIPT_OPENAI_API_KEY"; then
    all_set=false
fi

echo ""

if [ "$all_set" = false ]; then
    echo "❌ Missing required environment variables!"
    echo ""
    echo "Please set the following variables:"
    echo ""
    echo "  export YT_TRANSCRIPT_TELEGRAM_BOT_TOKEN=your_telegram_bot_token"
    echo "  export YT_TRANSCRIPT_YOUTUBE_API_KEY=your_youtube_api_key"
    echo "  export YT_TRANSCRIPT_OPENAI_API_KEY=your_openai_api_key"
    echo ""
    echo "Or source the .env.docker file after filling it:"
    echo "  cp .env.docker.example .env.docker"
    echo "  # Edit .env.docker with your values"
    echo "  source .env.docker"
    echo ""
    exit 1
fi

# Optional variables with defaults
if [ -z "$YT_TRANSCRIPT_DATABASE_URL" ]; then
    echo "ℹ️  YT_TRANSCRIPT_DATABASE_URL not set, using default: sqlite:///./data/bot.db"
fi

if [ -z "$YT_TRANSCRIPT_LOG_LEVEL" ]; then
    echo "ℹ️  YT_TRANSCRIPT_LOG_LEVEL not set, using default: INFO"
fi

echo ""
echo "✅ All checks passed!"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ docker-compose is not installed or not in PATH"
    exit 1
fi

echo "🐳 Starting Docker containers..."
echo ""

# Use docker compose or docker-compose depending on what's available
if docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Build and start
$DOCKER_COMPOSE up -d --build

echo ""
echo "✅ Bot started successfully!"
echo ""
echo "📊 View logs:"
echo "   $DOCKER_COMPOSE logs -f bot"
echo ""
echo "🛑 Stop bot:"
echo "   $DOCKER_COMPOSE down"
echo ""
echo "🔄 Restart bot:"
echo "   $DOCKER_COMPOSE restart bot"
echo ""

#!/bin/bash
# Development helper script for macOS

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if virtual environment is active
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo -e "${RED}❌ Virtual environment not activated!${NC}"
        echo -e "${YELLOW}Run: source venv/bin/activate${NC}"
        exit 1
    fi
}

# Function to start API server
start_api() {
    check_venv
    echo -e "${GREEN}🚀 Starting FastAPI server...${NC}"
    echo -e "${YELLOW}API Documentation: http://localhost:8000/docs${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Function to show CLI help
cli_help() {
    check_venv
    echo -e "${GREEN}🎵 YouTube Playlist Creator CLI${NC}"
    python -m app.cli --help
}

# Function to list CSV files
list_csv() {
    check_venv
    echo -e "${GREEN}�� Available CSV files:${NC}"
    python -m app.cli create --list-files
}

# Function to create playlist
create_playlist() {
    check_venv
    if [ -z "$1" ]; then
        echo -e "${YELLOW}Usage: ./scripts/dev.sh create filename.csv${NC}"
        list_csv
        exit 1
    fi
    python -m app.cli create --file "$1"
}

# Function to test services
test_services() {
    check_venv
    echo -e "${GREEN}🔧 Testing services...${NC}"
    python -m app.cli test
}

# Main command handling
case "$1" in
    "api")
        start_api
        ;;
    "cli")
        cli_help
        ;;
    "list")
        list_csv
        ;;
    "create")
        create_playlist "$2"
        ;;
    "test")
        test_services
        ;;
    *)
        echo -e "${GREEN}🎵 YouTube Playlist Creator - Development Helper${NC}"
        echo ""
        echo "Usage: ./scripts/dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  api     - Start FastAPI development server"
        echo "  cli     - Show CLI help"
        echo "  list    - List available CSV files"
        echo "  create  - Create playlist from CSV file"
        echo "  test    - Test all services"
        echo ""
        echo "Examples:"
        echo "  ./scripts/dev.sh api"
        echo "  ./scripts/dev.sh list"
        echo "  ./scripts/dev.sh create sample.csv"
        echo "  ./scripts/dev.sh test"
        ;;
esac

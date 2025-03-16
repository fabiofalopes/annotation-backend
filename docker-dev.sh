#!/bin/bash

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage
function show_usage {
    echo -e "${YELLOW}Usage:${NC} $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Build and start containers"
    echo "  stop        - Stop containers"
    echo "  restart     - Restart containers"
    echo "  rebuild     - Rebuild and restart containers"
    echo "  logs        - Show logs"
    echo "  clean       - Stop and remove containers, networks, and volumes"
    echo "  reset       - Complete reset (clean + remove images)"
    echo "  shell       - Open a shell in the API container"
    echo "  status      - Show container status"
    echo ""
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running.${NC}"
    exit 1
fi

# Process commands
case "$1" in
    start)
        echo -e "${GREEN}Starting containers...${NC}"
        docker-compose up -d
        ;;
    stop)
        echo -e "${GREEN}Stopping containers...${NC}"
        docker-compose down
        ;;
    restart)
        echo -e "${GREEN}Restarting containers...${NC}"
        docker-compose restart
        ;;
    rebuild)
        echo -e "${GREEN}Rebuilding and restarting containers...${NC}"
        docker-compose down
        docker-compose up -d --build
        ;;
    logs)
        echo -e "${GREEN}Showing logs...${NC}"
        docker-compose logs -f
        ;;
    clean)
        echo -e "${GREEN}Cleaning up containers, networks, and volumes...${NC}"
        docker-compose down -v
        ;;
    reset)
        echo -e "${GREEN}Complete reset (removing all containers, images, networks, and volumes)...${NC}"
        docker-compose down -v --rmi all
        ;;
    shell)
        echo -e "${GREEN}Opening shell in API container...${NC}"
        docker-compose exec api bash || docker-compose exec api sh
        ;;
    status)
        echo -e "${GREEN}Container status:${NC}"
        docker-compose ps
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

exit 0 
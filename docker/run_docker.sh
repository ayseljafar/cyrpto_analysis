#!/bin/bash

# Navigate to the docker directory
cd "$(dirname "$0")"

# Check if .env.docker exists
if [ ! -f .env.docker ]; then
    echo "Error: .env.docker file not found!"
    exit 1
fi

# Build and start the services
docker-compose up --build -d

# Show the logs
docker-compose logs -f 
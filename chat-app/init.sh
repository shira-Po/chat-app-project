#!/bin/bash

# Get the version from the user
echo "Enter the version:"
read version

# Build the Docker image with the provided version
docker build -t my-chatapp:${version} .

# Run the Docker container with the provided version
docker run --name chat-app -d -p 5000:5000 my-chatapp:${version}
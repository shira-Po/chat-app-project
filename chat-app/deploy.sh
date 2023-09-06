#!/bin/bash

# Check if the user has provided a version and commit hash
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: deploy.sh <version> <commit hash>"
  exit 1
fi

# Get the version and commit hash from the user
version=$1
commit_hash=$2

# Build the Docker image
docker build -t my-chatapp:${version} .

# Check if the Docker build was successful
if [ $? -ne 0 ]; then
  echo "Docker build failed"
  exit 1
fi

# Push the Docker image to GitHub Container Registry
echo "Pushing Docker image to GitHub Container Registry..."
docker push my-chatapp:${version}

# Tag the Docker image with the commit hash
docker tag my-chatapp:${version} my-chatapp:${commit_hash}


# Check if the Docker push was successful
if [ $? -ne 0 ]; then
  echo "Docker push failed"
  exit 1
fi

# Push to GitHub
git tag ${version}
git push origin ${version}

# Check if the Git push was successful
if [ $? -ne 0 ]; then
  echo "Git push failed"
  exit 1
fi

echo "Done!"

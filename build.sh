#!/bin/bash
set -e

RUNTIME_DEPS_DOCKERFILE="Dockerfile.runtime-deps"
RUNTIME_DEPS_IMAGE="ubuntu/dotnet-runtime-deps:test"
RUNTIME_DOCKERFILE="Dockerfile.runtime"
RUNTIME_IMAGE="ubuntu/dotnet-runtime:test"

echo "Building $RUNTIME_DEPS_DOCKERFILE..."
docker build -f $RUNTIME_DEPS_DOCKERFILE -t $RUNTIME_DEPS_IMAGE .

echo "Building $RUNTIME_DOCKERFILE Dockerfile..."
docker build -f $RUNTIME_DOCKERFILE -t $RUNTIME_IMAGE --build-arg RUNTIME_DEPS_IMAGE=$RUNTIME_DEPS_IMAGE .

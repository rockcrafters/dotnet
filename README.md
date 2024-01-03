# Chiselled .NET

Home for the Chiselled Ubuntu images for .NET, by Canonical.

## Images

### `ubuntu/dotnet-deps`

For those looking to run self-contained .NET applications. This is a tiny image
that only contains the minimal set of dependencies for running .NET, **but**
**not .NET itself**.

### `ubuntu/dotnet-runtime`

For those looking to run general-purpose .NET applications. This is a
minimalist image, with just the `dotnet-runtime-<version>` package and its
minimal set of dependencies.

### `ubuntu/dotnet-aspnet`

For those looking to run ASP.NET applications. This image inherits its content
from the `ubuntu/dotnet-deps` image and only adds the
`aspnetcore-runtime-<version>` package from the Ubuntu archives.

## About

**These images do not include bash or a package manager.**

Read more about Chiselled Ubuntu for .NET, a new class of OCI images, on [the Ubuntu blog](https://ubuntu.com/blog/install-dotnet-on-ubuntu); reading how Canonical and Microsoft partner together to deliver and support .NET on Ubuntu.


If you're looking to publish a self-contained .NET app, please have a look at the `ubuntu/dotnet-deps` repository.
If you're looking to publish an ASP.NET app, please then look at the `ubuntu/dotnet-aspnet` repository.

### Project Structure

This repository hosts all multiple Chiselled Ubuntu images for multiple
versions of .NET.

For automation and release purposes, different versions of .NET are maintained
in different **channel** branches:

- .NET 6.0: [`channels/6.0/edge`](https://github.com/ubuntu-rocks/dotnet/tree/channels/6.0/edge/dotnet-runtime)
- .NET 7.0: [`channels/7.0/edge`](https://github.com/ubuntu-rocks/dotnet/tree/channels/7.0/edge/dotnet-runtime)
- .NET 8.0: [`channels/8.0/edge`](https://github.com/ubuntu-rocks/dotnet/tree/channels/8.0/edge/dotnet-runtime)

The [central CI/CD pipelines](https://github.com/ubuntu-rocks/.build) that take
care of automating the build and release for these images, only looks at
"channel" branches named according to `channels/<version>/<risk>`.

Each channel branch will contain one or more Chiselled images.

You'll find more information about each Chiselled .NET image, as well as their
build recipes and tests, in each one of their corresponding channel branches.

## Building the .NET application image

These chiselled Ubuntu images are typically used as base images for building
one's application container image. For example:

```dockerfile
FROM ubuntu.azurecr.io/ubuntu:24.04 AS builder
# install the .NET 8 SDK from the Ubuntu archive
# (no need to clean the apt cache as this is an unpublished stage)
RUN apt-get update && apt-get install -y dotnet8 ca-certificates
# add your application code, e.g. for a "Hello" app
WORKDIR /source
COPY src/ .
# publish your .NET app
RUN dotnet publish -c Release -o /app

# Final chiselled image with the .NET application
FROM ubuntu.azurecr.io/dotnet-runtime:8.0-24.04_edge
WORKDIR /app
COPY --from=builder /app ./
EXPOSE 8080
ENTRYPOINT ["dotnet", "/app/Hello.dll"]
```

Similarly to the above, one can also add more package slices to an existing
chiselled Ubuntu image. Here's an example on how to add `libicu70` to an
`ubuntu/dotnet-deps` image:

```dockerfile
FROM ubuntu.azurecr.io/ubuntu:22.04 AS base
ARG TARGETARCH 
# Get the Chisel binary
ADD https://github.com/canonical/chisel/releases/download/v0.8.0/chisel_v0.8.0_linux_${TARGETARCH}.tar.gz chisel.tar.gz
RUN tar -xf chisel.tar.gz && \
    apt update && \
    apt install -y ca-certificates && \
    mkdir /rootfs && \
    ./chisel cut --root /rootfs libicu70_libs

# Final chiselled image with the libicu70 libraries
FROM ubuntu.azurecr.io/dotnet-deps:6.0-22.04_stable
COPY --from=base /rootfs /
```

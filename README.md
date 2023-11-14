# Chiselled .NET

Home for the Chiselled Ubuntu images for .NET, by Canonical.

## Images

### `ubuntu/dotnet-deps`

For those looking to run self-contained .NET applications. This is a tiny image
that only contains the minimal set of dependencies for running for .NET, **but**
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


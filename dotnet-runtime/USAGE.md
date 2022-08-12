# .NET runtime | Chiselled Ubuntu

.NET runtime image [from Canonical](https://ubuntu.com/security/docker-images), based on Ubuntu. Receives security updates and tracks the newest combination of .NET and Ubuntu LTS.     
**This repository is free to use and exempted from per-user rate limits.**


## About the .NET runtime

.NET is a free, cross-platform, open source developer platform for building many different types of applications. With .NET, you can use multiple languages, editors, and libraries to build for web, mobile, desktop, games, IoT, and more.
Read [the .NET documentation](https://docs.microsoft.com/en-us/dotnet/core/deploying/) to learn how to deploy your .NET application with container images.     

This image inherits its content from the `ubuntu/dotnet-deps` image and only adds the `dotnet-runtime-6.0` package from the Ubuntu archive.

**This image does not include bash nor a package manager nor the .NET SDK.**
Read more about Chiselled Ubuntu for .NET, a new class of OCI images, on [the Ubuntu blog](https://ubuntu.com/blog/install-dotnet-on-ubuntu); reading how Canonical and Microsoft partner together to deliver and support .NET on Ubuntu.

If you're looking to publish a self-contained .NET app, please have a look at the `ubuntu/dotnet-deps` repository.
If you're looking to publish an ASP.NET app, please then look at the `ubuntu/dotnet-aspnet` repository.


## Tags and Architectures
![LTS](https://assets.ubuntu.com/v1/0a5ff561-LTS%402x.png?h=17)
Up to 5 years free security maintenance on LTS channels.

![ESM](https://assets.ubuntu.com/v1/572f3fbd-ESM%402x.png?h=17)
Up to 10 years customer security maintenance `from canonical/dotnet-runtime`. [Request access](https://ubuntu.com/security/docker-images#get-in-touch).

_Tags in italics are not available in ubuntu/dotnet-runtime but are shown here for completeness._

| Channel Tag | | | Currently | Architectures |
|---|---|---|---|---|
 | `6.0-22.10_edge` &nbsp;&nbsp; |  | | .NET runtime 6.0 on Ubuntu&nbsp;22.10&nbsp;| `amd64` |
 | **`6.0-22.04_beta`** &nbsp;&nbsp; | ![LTS](https://assets.ubuntu.com/v1/0a5ff561-LTS%402x.png?h=17) | | .NET runtime 6.0 on Ubuntu&nbsp;22.04&nbsp;LTS| `amd64` |
| _`track_risk`_ |

Channel Tag shows the most stable channel for that track. A track is a combination of both the application version and the underlying Ubuntu series, eg `1.0-22.04`.     
Channels are ordered from the most stable to the least `stable`, `candidate`, `beta`, `edge`. More risky channels are always implicitly available. So if `beta` is listed, you can also pull `edge`. If `candidate` is listed, you can pull `beta` and `edge`. When `stable` is listed, all four are available. Images are guaranteed to progress through the sequence `edge`, `beta`, `candidate` before `stable`.

### Commercial use and Extended Security Maintenance channels
If your usage includes commercial redistribution or requires unavailable channels/versions, please [get in touch with the Canonical team](https://ubuntu.com/security/docker-images#get-in-touch) (or writing to rocks@canonical.com).

## Usage

Use this image to layer your .NET application relying on dependencies sourced from the Ubuntu distribution.

See the following multi-stage Dockerfile, building a .NET 6 app on Ubuntu 22.04
and packaging it on top of `ubuntu/dotnet-runtime:6.0-22.04_beta`:

```Dockerfile
# Adapting the example code on
# https://github.com/dotnet/samples/tree/main/core/console-apps/FibonacciBetterMsBuild
# to use .NET 6 (<TargetFramework>net6.0</TargetFramework>)

FROM ubuntu:22.04 AS builder

# install the .NET 6 SDK from the Ubuntu archive
# (no need to clean the apt cache as this is an unpublished stage)
RUN apt-get update && apt-get install -y dotnet6 ca-certificates

# add your application code
WORKDIR /source
COPY . .

# publish your .NET app
RUN dotnet publish -c Release -o /app

FROM ubuntu/dotnet-runtime:6.0-22.04_beta

WORKDIR /app
COPY --from=builder /app ./

ENV PORT 8080
EXPOSE 8080

ENTRYPOINT ["dotnet", "/app/Fibonacci.dll"]
```

<!-- 
#### Parameters

| Parameter | Description |
|---|---|
| `-e TZ=UTC` | Timezone. | -->

## Bugs and feature requests

If you find a bug in our image or want to request a specific feature, please file a bug here:

[https://bugs.launchpad.net/ubuntu-docker-images/+filebug](https://bugs.launchpad.net/ubuntu-docker-images/+filebug)

Please title the bug "`dotnet-runtime: <issue summary>`". Make sure to include the digest of the image you are using, from:

```sh
docker images --no-trunc --quiet ubuntu/dotnet-runtime:<tag>
```


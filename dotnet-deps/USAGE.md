# .NET deps | Chiselled Ubuntu

.NET deps image [from Canonical](https://ubuntu.com/security/docker-images), based on Ubuntu. Receives security updates and tracks the newest combination of .NET and Ubuntu LTS.     
**This repository is free to use and exempted from per-user rate limits.**


## About .NET deps

The .NET deps image is a clean base image for developers to layer their self-contained .NET and ASP.NET applications. Read [the .NET documentation](https://docs.microsoft.com/en-us/dotnet/core/deploying/).     
It only includes the runtime dependencies required to run a standard self-contained .NET application: `ca-certificates`, `libc6`, `libgcc`, `libssl3`, `libstdc++6`, and `zlib1g`.     

**This image does not include bash nor a package manager.**
Read more about Chiselled Ubuntu for .NET, a new class of OCI images, on [the Ubuntu blog](https://ubuntu.com/blog/install-dotnet-on-ubuntu).         

Canonical and Microsoft [partner together](https://ubuntu.com/blog/install-dotnet-on-ubuntu) to deliver and support .NET on Ubuntu.

If you're looking for the .NET or the ASP.NET runtime images, please have a look at the `ubuntu/dotnet-runtime` and `ubuntu/dotnet-aspnet` repositories.


## Tags and Architectures
![LTS](https://assets.ubuntu.com/v1/0a5ff561-LTS%402x.png?h=17)
Up to 5 years free security maintenance on LTS channels.

![ESM](https://assets.ubuntu.com/v1/572f3fbd-ESM%402x.png?h=17)
Up to 10 years customer security maintenance `from canonical/dotnet-deps`. [Request access](https://ubuntu.com/security/docker-images#get-in-touch).

_Tags in italics are not available in ubuntu/dotnet-deps but are shown here for completeness._

| Channel Tag | | | Currently | Architectures |
|---|---|---|---|---|
 | `6.0-22.10_beta` &nbsp;&nbsp; |  | | .NET deps 6.0 on Ubuntu&nbsp;22.10&nbsp;| `amd64`, `arm64`, `ppc64el`, `s390x` |
 | **`6.0-22.04_beta`** &nbsp;&nbsp; | ![LTS](https://assets.ubuntu.com/v1/0a5ff561-LTS%402x.png?h=17) | | .NET deps 6.0 on Ubuntu&nbsp;22.04&nbsp;LTS| `amd64`, `arm64`, `ppc64el`, `s390x` |
| _`track_risk`_ |

Channel Tag shows the most stable channel for that track. A track is a combination of both the application version and the underlying Ubuntu series, eg `1.0-22.04`.     
Channels are ordered from the most stable to the least `stable`, `candidate`, `beta`, `edge`. More risky channels are always implicitly available. So if `beta` is listed, you can also pull `edge`. If `candidate` is listed, you can pull `beta` and `edge`. When `stable` is listed, all four are available. Images are guaranteed to progress through the sequence `edge`, `beta`, `candidate` before `stable`.

### Commercial use and Extended Security Maintenance channels
If your usage includes commercial redistribution or requires unavailable channels/versions, please [get in touch with the Canonical team](https://ubuntu.com/security/docker-images#get-in-touch) (or writing to rocks@canonical.com).

## Usage

Use this image to layer your self-contained .NET or ASP.NET application.

See the following multi-stage Dockerfile, building an ASP.NET app on Ubuntu 22.04
and packaging it on top of `ubuntu/dotnet-deps:6.0-22.04_beta`:

```Dockerfile
FROM ubuntu:22.04 AS builder

# install the .NET 6 SDK from the Ubuntu archive
# (no need to clean the apt cache as this is an unpublished stage)
RUN apt-get update && apt-get install -y dotnet6 ca-certificates

# add your application code
WORKDIR /source
# using https://github.com/Azure-Samples/dotnetcore-docs-hello-world
COPY . .

# export your .NET app as a self-contained artefact
RUN dotnet publish -c Release -r ubuntu.22.04-x64 --self-contained true -o /app

FROM ubuntu/dotnet-deps:6.0-22.04_beta

WORKDIR /app
COPY --from=builder /app ./

ENV PORT 8080
EXPOSE 8080

ENTRYPOINT ["/app/dotnetcoresample"]
```

Run the following commands with the Dockerfile example from above:

```sh
git clone https://github.com/Azure-Samples/dotnetcore-docs-hello-world
cd dotnetcore-docs-hello-world
# copy the content from the example above into ./Dockerfile
docker build -t my-dotnet-app-chiseled-ubuntu:22.04 .
```

<!-- 
#### Parameters

| Parameter | Description |
|---|---|
| `-e TZ=UTC` | Timezone. | -->

## Bugs and feature requests

If you find a bug in our image or want to request a specific feature, please file a bug here:

[https://bugs.launchpad.net/ubuntu-docker-images/+filebug](https://bugs.launchpad.net/ubuntu-docker-images/+filebug)

Please title the bug "`dotnet-deps: <issue summary>`". Make sure to include the digest of the image you are using, from:

```sh
docker images --no-trunc --quiet ubuntu/dotnet-deps:<tag>
```


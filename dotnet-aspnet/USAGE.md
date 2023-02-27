# Chiselled Ubuntu for ASP.NET

ASP.NET runtime image [from Canonical](https://ubuntu.com/security/docker-images), based on Ubuntu. Receives security updates and tracks the newest combination of ASP.NET and Ubuntu LTS.
**This repository is free to use and exempted from per-user rate limits.**


## About the ASP.NET runtime

ASP.NET is an open source web framework, created by Microsoft, for building modern web apps and services with .NET.
Read [the .NET documentation](https://docs.microsoft.com/en-us/dotnet/core/deploying/) to learn how to deploy your .NET application with container images.

This image inherits its content from the `ubuntu/dotnet-deps` image and only adds the `aspnetcore-runtime-7.0` package from the Ubuntu archive.

### About chiselled Ubuntu containers

**This image does not include bash nor a package manager nor the .NET SDK.**
Read more about Chiselled Ubuntu for .NET, a new class of OCI images, on [the Ubuntu blog](https://ubuntu.com/blog/install-dotnet-on-ubuntu); reading how Canonical and Microsoft partner together to deliver and support .NET on Ubuntu.

If you're looking to publish a self-contained .NET app, please have a look at the `ubuntu/dotnet-deps` repository.
If you're looking for the .NET runtime (without ASP.NET), please then look at the `ubuntu/dotnet-runtime` repository.


## Tags and Architectures
![LTS](https://assets.ubuntu.com/v1/0a5ff561-LTS%402x.png?h=17)
Up to 5 years free security maintenance on LTS channels.

![ESM](https://assets.ubuntu.com/v1/572f3fbd-ESM%402x.png?h=17)
Up to 10 years customer security maintenance `from canonical/dotnet-aspnet`. [Request access](https://ubuntu.com/security/docker-images#get-in-touch).

_Tags in italics are not available in ubuntu/dotnet-aspnet but are shown here for completeness._

| Channel Tag | | | Currently | Architectures |
|---|---|---|---|---|
 | `7.0-22.10_edge` &nbsp;&nbsp; |  | | ASP.NET 7.0 on Ubuntu&nbsp;22.10&nbsp;| `amd64` |
| _`track_risk`_ |

Channel Tag shows the most stable channel for that track. A track is a combination of both the application version and the underlying Ubuntu series, eg `1.0-22.04`.
Channels are ordered from the most stable to the least `stable`, `candidate`, `beta`, `edge`. More risky channels are always implicitly available. So if `beta` is listed, you can also pull `edge`. If `candidate` is listed, you can pull `beta` and `edge`. When `stable` is listed, all four are available. Images are guaranteed to progress through the sequence `edge`, `beta`, `candidate` before `stable`.

### Commercial use and Extended Security Maintenance channels
If your usage includes commercial redistribution or requires unavailable channels/versions, please [get in touch with the Canonical team](https://ubuntu.com/security/docker-images#get-in-touch) (or writing to rocks@canonical.com).

## Usage

Use this image to layer your ASP.NET application relying on dependencies sourced from the Ubuntu distribution.

See the following multi-stage Dockerfile, building an ASP.NET 7 app on Ubuntu 22.10
and packaging it on top of `ubuntu/dotnet-aspnet:7.0-22.10_beta`:

```Dockerfile
FROM ubuntu.azurecr.io/ubuntu:22.10 AS builder

# install the .NET 7 SDK from the Ubuntu archive
# (no need to clean the apt cache as this is an unpublished stage)
RUN apt-get update && apt-get install -y dotnet7 ca-certificates

# add your application code
WORKDIR /source
# using https://github.com/Azure-Samples/dotnetcore-docs-hello-world
COPY . .

# publish your ASP.NET app
RUN dotnet publish -c Release -o /app --self-contained false

FROM ubuntu.azurecr.io/dotnet-aspnet:7.0-22.10_edge

WORKDIR /app
COPY --from=builder /app ./

ENTRYPOINT ["dotnet", "/app/dotnetcoresample.dll"]
```

Run the following commands with the Dockerfile example from above:

```sh
git clone https://github.com/Azure-Samples/dotnetcore-docs-hello-world
cd dotnetcore-docs-hello-world
# copy the content from the example above into ./Dockerfile
docker build . -t my-chiseled-aspnet-app:latest
docker run -p 8080:8080 my-chiseled-aspnet-app:latest
# access http://localhost:8080/
```

<!-- 
#### Parameters

| Parameter | Description |
|---|---|
| `-e TZ=UTC` | Timezone. | -->

## Bugs and feature requests

If you find a bug in our image or want to request a specific feature, please file a bug here:

[https://bugs.launchpad.net/ubuntu-docker-images/+filebug](https://bugs.launchpad.net/ubuntu-docker-images/+filebug)

Please title the bug "`dotnet-aspnet: <issue summary>`". Make sure to include the digest of the image you are using, from:

```sh
docker images --no-trunc --quiet ubuntu/dotnet-aspnet:<tag>
```


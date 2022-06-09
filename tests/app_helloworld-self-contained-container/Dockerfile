ARG DOTNET_RUNTIME_DEPS_IMAGE="ubuntu/dotnet-runtime-deps:test"

FROM ubuntu:22.04 AS dotnet
RUN set -eu -x ;\
    export DEBIAN_FRONTEND=noninteractive ;\
    apt-get update ;\
    apt-get install -y curl rsync ca-certificates ;\
    curl -fsS -o /usr/share/keyrings/cloud-images-ubuntu-dotnet.asc \
    "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xDA865DE20313CD8EA97063C75E700FE3D36CFC37" ;\
    . /etc/os-release ;\
    echo "deb [signed-by=/usr/share/keyrings/cloud-images-ubuntu-dotnet.asc] https://ppa.launchpadcontent.net/cloud-images/dotnet/ubuntu/ $UBUNTU_CODENAME main" \
    >/etc/apt/sources.list.d/cloud-images-ubuntu-dotnet.list ;\
    apt-get update ;\
    apt-get install -y dotnet6 ;\
    :
RUN set -eux ;\
    dotnet_home=$(readlink -f /usr/lib/dotnet/dotnet6) ;\
    rsync -aRr \
    $dotnet_home/dotnet \
    $dotnet_home/host/ \
    $dotnet_home/install_location \
    $dotnet_home/install_location_x64 \
    $dotnet_home/shared/ \
    /etc/alternatives/dotnet \
    /etc/alternatives/install_location \
    /etc/alternatives/install_location_x64 \
    /etc/dotnet/ \
    /usr/bin/dotnet \
    /usr/lib/dotnet/dotnet6 \
    /dotnet-runtime ;\
    :
COPY src /app
WORKDIR /app
RUN dotnet publish -r linux-x64 

FROM ${DOTNET_RUNTIME_DEPS_IMAGE}
COPY --from=dotnet /app/bin /app/bin
COPY --from=dotnet /app/obj /app/obj
ENTRYPOINT [ "/app/bin/Debug/net6.0/linux-x64/Hello" ]

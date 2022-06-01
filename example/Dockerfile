FROM ubuntu:jammy AS dotnet
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

FROM golang as chisel-build
WORKDIR /go
RUN set -eu -x ;\
  git clone https://github.com/canonical/chisel ;\
  cd chisel/cmd/chisel ;\
  CGO_ENABLED=0 go build ;\
  :

FROM dotnet AS prep
COPY release /release
COPY --from=chisel-build /go/chisel/cmd/chisel/chisel /bin/chisel
COPY release /release
WORKDIR /target
RUN set -eu -x ;\
  chisel cut --release /release --root . \
    base-files_all \
    libc6_libs \
    libgcc-s1_libs \
    libssl3_libs \
    libstdc++6_libs \
    zlib1g_libs \
    ca-certificates_all
# fixes
RUN set -eu -x ;\
  chmod 1777 tmp ;\
  echo root:!:0:0:root:/:/nonexistent >etc/passwd ;\
  echo root:x:0: >etc/group ;\
  :

FROM scratch
COPY --from=prep /target /
COPY --from=dotnet /dotnet-runtime /
COPY --from=dotnet /etc/ssl/certs /etc/ssl/certs
ENV DOTNET_RUNNING_IN_CONTAINER=true DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true

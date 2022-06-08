ARG ROOTFS=/rootfs

FROM ubuntu:22.04 as builder
ARG ROOTFS
WORKDIR ${ROOTFS}
RUN set -eu -x; \
    apt update; \
    apt install -y golang git; \
    useradd app; \
    mkdir /home/app; \
    chown -R app:app ${ROOTFS} /home/app 
COPY install-slices .
USER app
RUN mkdir -p output ; \
    git clone --depth 1 -b main https://github.com/canonical/chisel chisel ; \
    cd chisel/cmd/chisel ; \
    go build ; \
    # TODO: remove this once the respective chisel-release is upstream 
    git clone -b ubuntu-22.04 https://github.com/woky/chisel-releases ; \
    ./chisel cut --release chisel-releases --root ${ROOTFS}/output $(cat ${ROOTFS}/install-slices) ; \
    mkdir -p ${ROOTFS}/output/etc ; \
    cat /etc/passwd | tail -1 > ${ROOTFS}/output/etc/passwd ; \
    cat /etc/group | tail -1 > ${ROOTFS}/output/etc/group

FROM scratch 
ARG ROOTFS
COPY --from=builder $ROOTFS/output /
ENV \
    # Configure web servers to bind to port 80 when present
    ASPNETCORE_URLS=http://+:80 \
    # Enable detection of running in a container
    DOTNET_RUNNING_IN_CONTAINER=true \
    # Set the invariant mode since ICU package isn't included (see https://github.com/dotnet/announcements/issues/20)
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true
USER app
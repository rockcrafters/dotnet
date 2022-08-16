#!/usr/bin/env python3

import argparse
import glob
import hashlib
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import yaml
from pathlib import Path

SUPPORTED_ARCHS = ["amd64", "arm", "arm64", "s390x", "ppc64le"]

MACHINE_TO_ARCH = {"x86_64": "amd64"}

build_outputs_dir = "_build"
shutil.rmtree(build_outputs_dir, ignore_errors=True)
os.mkdir(build_outputs_dir)


class PlatformValidationError(Exception):
    """Error when provided platforms cannot be validated"""


def prepare_for_build(rockcraft_yaml: str) -> tuple:
    """Parses ROCK project and return attributes for build"""
    with open(rockcraft_yaml, encoding="utf-8") as yaml_file:
        # Need to use BaseLoader here to avoid value conversion
        # SafeLoader would fetch "base" as a number, which in turn
        # would make bases like 22.10 be parsed as 22.1
        yaml_data = yaml.load(yaml_file, Loader=yaml.BaseLoader)

    rock_name = yaml_data["name"]
    rock_base = yaml_data["base"]
    rock_version = yaml_data["version"]
    dockerfile_path = f"{rock_name}/Dockerfile.{rock_base}"
    rock_build_for = []
    for platform_label, platform_values in yaml_data["platforms"].items():
        if not platform_values:
            platform_values = {}

        build_for = list(platform_values.get("build-for", [platform_label]))

        if platform_label in SUPPORTED_ARCHS and [platform_label] != build_for:
            msg = (
                f"{rockcraft_yaml}: "
                f"the provided platform label '{platform_label}' is valid, "
                f"but different from the provided build-for: {build_for}"
            )
            raise PlatformValidationError(msg)

        if not all([arch in SUPPORTED_ARCHS for arch in build_for]):
            msg = (
                f"{rockcraft_yaml}: "
                f"the provided target platform '{build_for}' is not supported. "
                f"Supported target architectures are: {SUPPORTED_ARCHS}"
            )
            raise PlatformValidationError(msg)

        if platform_values.get("build-for") and not platform_values.get("build-on"):
            msg = (
                f"{rockcraft_yaml}: "
                f"in platform label '{platform_label}', if 'build-for' is provided "
                "then 'build-on' must also be defined."
            )
            raise PlatformValidationError(msg)

        build_on = list(platform_values.get("build-on", [platform_label]))
        if not all([arch in SUPPORTED_ARCHS for arch in build_on]):
            msg = (
                f"{rockcraft_yaml}: "
                f"the provided build platform '{build_on}' is not supported. "
                f"Supported build architectures are: {MACHINE_TO_ARCH.values()}"
            )
            raise PlatformValidationError(msg)

        if not any(
            [
                MACHINE_TO_ARCH.get(platform.machine()) == build_on_arch
                for build_on_arch in build_on
            ]
        ):
            msg = (
                f"{rockcraft_yaml}: "
                f"none of the provided 'build-on' architectures ({build_on}) for the platform "
                f"label {platform_label} are compatible with the underlying "
                f"build machine architecture: {platform.machine()} (aka {MACHINE_TO_ARCH.get(platform.machine())})"
            )
            logging.warning(msg)
            # raise PlatformValidationError(msg)

        rock_build_for += build_for

    return rock_name, rock_version, rock_base, rock_build_for, dockerfile_path


def build_rock(
    dockerfile: str,
    oci_archive_name: str,
    rock_build_for: list,
    rock_name: str,
    tag_name: str,
) -> None:
    """Run Docker buildx build"""
    build_cmd = [
        "docker",
        "buildx",
        "build",
        f"--file={dockerfile}",
        f"--output=type=oci,dest={oci_archive_name}",
        f"--platform={','.join(map(lambda p: f'linux/{p}', rock_build_for))}",
        f"--tag={rock_name}:{tag_name}",
        rock_name,
    ]
    logging.info(f"Building {tag_name} into {oci_archive_name}...")
    logging.info(f" ---> {' '.join(build_cmd)}")
    subprocess.check_output(build_cmd)
    logging.info(f"Successfully built new ROCK {oci_archive_name}!")


def convert_to_oci(archive: str, dst: str) -> None:
    """Skopeo copy from archive to oci"""
    copy_cmd = [
        "skopeo",
        "--insecure-policy",
        "copy",
        "--multi-arch",
        "all",
        "--preserve-digests",
        f"oci-archive:{archive}",
        f"oci:{dst}",
    ]
    logging.info(f"Copying oci-archive:{archive} into oci:{dst}...")
    logging.info(f" ---> {' '.join(copy_cmd)}")
    subprocess.check_output(copy_cmd)
    logging.info(f"Successfully converted OCI archive into OCI, at {dst}!")


def inject_variant(oci_img: str, for_arch: str, variant: str) -> None:
    """Adds variant to OCI image with the specified arch."""
    logging.info(
        str(
            " ----- "
            f"Inject variant {variant}, if needed, "
            f"on image {oci_img}, for arch {for_arch}..."
        )
    )
    tl_index_path_ = Path(f"{oci_img}/index.json")
    tl_index_ = json.loads(tl_index_path_.read_bytes())

    manifest_list_digest = tl_index_["manifests"][0]["digest"].split(":")[-1]
    manifest_list_path_ = Path(f"{oci_img}/blobs/sha256/{manifest_list_digest}")
    logging.info(f"Checking manifest list {manifest_list_path_}")

    manifest_list_content_ = json.loads(manifest_list_path_.read_bytes())
    manifest_list_media_type = manifest_list_content_["mediaType"]

    manifest_content_ = manifest_list_content_
    manifest_path_ = manifest_list_path_

    if manifest_list_media_type == "application/vnd.oci.image.index.v1+json":
        logging.info("Dealing with a multi-arch image...")
        for manifest_number, manifest_entry in enumerate(
            manifest_list_content_["manifests"]
        ):
            if manifest_entry["platform"][
                "architecture"
            ] == for_arch and not manifest_entry["platform"].get("variant"):
                manifest_digest = manifest_entry["digest"].split(":")[-1]
                manifest_path_ = Path(f"{oci_img}/blobs/sha256/{manifest_digest}")
                manifest_content_ = json.loads(manifest_path_.read_bytes())

                break

    image_config_digest = manifest_content_["config"]["digest"].split(":")[-1]
    image_config_path_ = Path(f"{oci_img}/blobs/sha256/{image_config_digest}")
    img_config_content_ = json.loads(image_config_path_.read_bytes())
    if img_config_content_["architecture"] != for_arch:
        logging.info(
            f"The image {oci_img} does not have a manifest for arch {for_arch}. Nothing to do..."
        )
        return

    img_config_content_["variant"] = variant
    logging.info(f"Removing OCI image config {image_config_path_}...")
    os.remove(image_config_path_)
    config_bytes = json.dumps(img_config_content_).encode("utf-8")
    config_digest = hashlib.sha256(config_bytes).hexdigest()
    image_config_path_ = Path(f"{oci_img}/blobs/sha256/{config_digest}")
    image_config_path_.write_bytes(config_bytes)
    logging.info(
        f"New OCI image config at {image_config_path_}, with variant {variant}."
    )

    manifest_content_["config"]["digest"] = f"sha256:{config_digest}"
    manifest_content_["config"]["size"] = len(config_bytes)
    logging.info(f"Removing manifest {manifest_path_}...")
    os.remove(manifest_path_)
    manifest_bytes = json.dumps(manifest_content_).encode("utf-8")
    manifest_digest = hashlib.sha256(manifest_bytes).hexdigest()
    new_manifest_path_ = Path(f"{oci_img}/blobs/sha256/{manifest_digest}")
    new_manifest_path_.write_bytes(manifest_bytes)
    logging.info(
        f"New OCI manifest {new_manifest_path_}, for new OCI img config {image_config_path_}."
    )

    if manifest_path_ != manifest_list_path_:
        logging.debug("Also updating the manifest list content...")

        manifest_entry["digest"] = f"sha256:{manifest_digest}"
        manifest_entry["size"] = len(manifest_bytes)
        manifest_entry["platform"]["variant"] = variant
        manifest_list_content_["manifests"][manifest_number] = manifest_entry
        logging.info(f"Removing manifest list {manifest_list_path_}...")
        os.remove(manifest_list_path_)
        manifest_bytes = manifest_list_bytes = json.dumps(
            manifest_list_content_
        ).encode("utf-8")
        manifest_digest = manifest_list_digest = hashlib.sha256(
            manifest_list_bytes
        ).hexdigest()
        manifest_list_path_ = Path(f"{oci_img}/blobs/sha256/{manifest_list_digest}")
        manifest_list_path_.write_bytes(manifest_list_bytes)
        logging.info(
            f"New OCI manifest list {manifest_list_path_}, which includes new manifest {new_manifest_path_}."
        )

    tl_index_["manifests"][0]["digest"] = f"sha256:{manifest_digest}"
    tl_index_["manifests"][0]["size"] = len(manifest_bytes)
    logging.info(f"Rewriting {tl_index_path_}, to point to manifest {manifest_digest}")
    os.remove(tl_index_path_)
    tl_index_path_.write_bytes(json.dumps(tl_index_).encode("utf-8"))


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

parser = argparse.ArgumentParser(description="Manual image builder and releaser")
parser.add_argument(
    "--risk",
    required=True,
    help="risk under which to publish the ROCK. Default: edge",
)
parser.add_argument(
    "--rockcraft-files",
    default=None,
    help="comma-separated list of Rockcraft YAML files to build from. Default: all in this path",
)
parser.add_argument(
    "--additional-tags",
    default="",
    help="comma-separated list of additional OCI tags for each ROCK",
)
args = parser.parse_args()


rockcraft_projects = (
    glob.glob("rockcraft*.yaml")
    if not args.rockcraft_files
    else args.rockcraft_files.split(",")
)

rockcraft_projects.sort()
for rock_project in rockcraft_projects:
    logging.info(f"Prepare to build from {rock_project}")
    rock_name, rock_version, rock_base, rock_build_for, dockerfile = prepare_for_build(
        rock_project
    )

    oci_archive_name = (
        f"{build_outputs_dir}/{rock_name}_{rock_version}_{rock_base}_{args.risk}.rock"
    )

    tag_name = f"{rock_version}-{rock_base}_{args.risk}"

    build_rock(dockerfile, oci_archive_name, rock_build_for, rock_name, tag_name)
    oci_name = oci_archive_name.rstrip(".rock")
    convert_to_oci(oci_archive_name, oci_name)

    # fix_img_config_for = [
    #     {
    #         "where": {"architecture": "arm64", "variant": None},
    #         "change_to": {"architecture": "arm64", "variant": "v8"},
    #     },
    #     {
    #         "where": {"architecture": "arm", "variant": None},
    #         "change_to": {"architecture": "arm", "variant": "v7"},
    #     },
    # ]
    inject_variant(oci_name, "arm64", "v8")

    # push to registries
    # localhost must be already authenticated
    publish_to = [
        # Docker Hub
        "ubuntu/",
        # ACR
        "ubuntu.azurecr.io/",
    ]

    logging.info(" ----- PUBLISHING TO -----")
    for repo in publish_to:
        raw_cmd = str(
            f"skopeo --insecure-policy copy --preserve-digests oci:{oci_name}"
        )
        logging.info(f"  --> {repo}{rock_name}:{tag_name}")

        raw_cmd_push = (
            f"{raw_cmd} --multi-arch all docker://{repo}{rock_name}:{tag_name}"
        )
        subprocess.check_output(raw_cmd_push.split())
        for add_tag in args.additional_tags.split(","):
            logging.info(
                f"Adding additional tag {add_tag} to {rock_name}, pointing to {tag_name}"
            )
            raw_cmd_tag = f"{raw_cmd} --multi-arch index-only docker://{repo}{rock_name}:{add_tag}"

            subprocess.check_output(raw_cmd_tag.split())


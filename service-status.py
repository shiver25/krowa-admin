#!/usr/bin/env python3


import argparse
import os
os.system("")
import shutil
import subprocess
import yaml
from pathlib import Path
from checks.docker import get_docker_container_report
from checks.k3s import check_k3s_token, get_k3s_status, get_namespace_report
from checks.services import check_service_status
from checks.system_resources import (
    get_disk_report,
    get_load_report,
    get_memory_report,
    get_uptime_report,
)
from formatting import COLORS, print_section_title, print_section_header


SCRIPT_PATH = Path(__file__).resolve()


def parse_args():
    parser = argparse.ArgumentParser()

    modes = parser.add_mutually_exclusive_group()

    modes.add_argument(
        "--summary",
        action="store_const",
        const="summary",
        dest="mode",
        help="Show compact result and problem details",
    )

    modes.add_argument(
        "--only-problems",
        action="store_const",
        const="problems",
        dest="mode",
        help="Show only warnings and errors",
    )

    parser.set_defaults(mode="full")

    return parser.parse_args()

def load_config(path="/etc/krowa-admin/config.yaml"):
    try:
        with open(path, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file) or {}

    except FileNotFoundError:
        print(f"Error: config file {path} was not found.")
        return {}

    except PermissionError:
        print(f"Error: no permission to read {path}.")
        return {}

    except yaml.YAMLError as error:
        print(f"Error: invalid YAML in {path}: {error}")
        return {}

    if not isinstance(config, dict):
        print(f"Error: config root in {path} must be a mapping.")
        return {}

    return config


config = load_config()
services_config = config.get("checks", {}).get("services", {})
docker_config = config.get("checks", {}).get("docker_containers", {})
k3s_config = config.get("checks", {}).get("k3s", {})
system_resources_config = (
    config.get("checks", {})
    .get("system_resources", {})
)


def generate_status_report(mode="full"):
    """Generuje raport o statusie usług"""
    report = "\n"
    report += print_section_header("KROWA ADMIN")

    if system_resources_config.get("enabled", False):
        system_reports = []
        uptime_config = system_resources_config.get("uptime", {})

        if uptime_config.get("enabled", False):
            system_reports.append(
                get_uptime_report().rstrip()
            )

        load_settings = system_resources_config.get("load", {})

        if load_settings.get("enabled", False):
            system_reports.append(
                get_load_report().rstrip()
            )

        memory_settings = system_resources_config.get("memory", {})

        if memory_settings.get("enabled", False):
            system_reports.append(
                get_memory_report().rstrip()
            )

        disk_settings = system_resources_config.get(
            "disk",
            {},
        )

        if disk_settings.get("enabled", False):
            system_reports.append(
                get_disk_report(disk_settings).rstrip()
            )


        if system_reports:
            report += print_section_title("SYSTEM")
            report += "\n\n".join(system_reports)
            report += "\n"

    if services:
        report += print_section_title("SERVICES")
        for service in services:
            status_str = f"{COLORS['green']}✔ running{COLORS['reset']}" if check_service_status(service) else f"{COLORS['red']}✖ not running{COLORS['reset']}"
            report += f"{service}: {status_str}\n"

    if docker_config.get("enabled", False):
      report += get_docker_container_report(
          docker_config,
          mode=mode,
      )

    if k3s_config.get("enabled", False):
      if check_service_status("k3s"):
        report += get_k3s_status()

        namespaces_config = k3s_config.get("namespaces", {})
        if namespaces_config.get("enabled", False):
            report += get_namespace_report(namespaces_config)
      else:
          report += (
            f"{COLORS['red']}✖ K3s is not running"
            f"{COLORS['reset']}\n"
          )

      token_config = k3s_config.get("token", {})
      if token_config.get("enabled", False):
          report += check_k3s_token(token_config)

    report += (
      f"\n{COLORS['cyan']}"
      f"(This script is located at: {SCRIPT_PATH})"
      f"{COLORS['reset']}"
    )

    report += f"\n{COLORS['cyan']}(Triggered by: /etc/profile.d/krowa-admin.sh){COLORS['reset']}\n"
    
    return report

if __name__ == "__main__":
    args = parse_args()

    if services_config.get("enabled", False):
        services = services_config.get("items", [])
    else:
        services = []

    report = generate_status_report(mode=args.mode)
    print(report)

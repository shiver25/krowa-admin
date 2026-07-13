#!/usr/bin/env python3


import os
os.system("")
import shutil
import subprocess
import yaml
from pathlib import Path
from checks.docker import get_docker_container_report
from checks.k3s import check_k3s_token, get_k3s_status, get_namespace_report
from checks.services import check_service_status
from formatting import COLORS, print_section_title, print_section_header


SCRIPT_PATH = Path(__file__).resolve()


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



def generate_status_report():
    """Generuje raport o statusie usług"""
    report = "\n"
    report += print_section_header("KROWA ADMIN")
    report += print_section_title("SERVICE STATUS REPORT")
    for service in services:
        status_str = f"{COLORS['green']}✔ running{COLORS['reset']}" if check_service_status(service) else f"{COLORS['red']}✖ not running{COLORS['reset']}"
        report += f"{service}: {status_str}\n"

    if docker_config.get("enabled", False):
      report += get_docker_container_report(docker_config)

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

    if services_config.get("enabled", False):
        services = services_config.get("items", [])
    else:
        services = []

    report = generate_status_report()
    print(report)


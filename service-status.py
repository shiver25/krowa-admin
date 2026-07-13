#!/usr/bin/env python3

# Service Status Script
# This script is executed at login via /etc/profile.d/service-status.sh
# Located at: /usr/local/bin/service-status.py

# ==============================================
# ANSI Escape Codes - Colors for terminal output
# ==============================================
# \033[0m       Reset color
# \033[1;31m    Red (errors, warnings)
# \033[1;32m    Green (success, running)
# \033[1;33m    Yellow (warnings, caution)
# \033[1;34m    Blue (headers, titles)
# \033[1;35m    Magenta (unused, but available)
# \033[1;36m    Cyan (info, file paths)
# \033[1;37m    White (can be used for contrast)
#
# Example usage:
#   print(f"{COLORS['blue']}This is a blue header{COLORS['reset']}")
#   print(f"{COLORS['green']}✔ Service running{COLORS['reset']}")
#   print(f"{COLORS['red']}✖ Service not running{COLORS['reset']}")


import os
os.system("")
import shutil
import subprocess
import yaml


def load_config(path="/etc/krowa-admin/config.yaml"):
    with open(path, "r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)

config = load_config()
services_config = config.get("checks", {}).get("services", {})
docker_config = config.get("checks", {}).get("docker_containers", {})
k3s_config = config.get("checks", {}).get("k3s", {})


# ANSI Escape Codes - Colors
COLORS = {
    "reset": "\033[0m",
    "red": "\033[1;31m",
    "green": "\033[1;32m",
    "yellow": "\033[1;33m",
    "blue": "\033[1;34m",
    "magenta": "\033[1;35m",
    "cyan": "\033[1;36m",
    "white": "\033[1;37m",
}


def print_section_header(title):
    """Generuje nagłówek sekcji w raporcie"""
    line = "=" * 40
    title = f" {title} "
    padding = (40 - len(title)) // 2
    extra_padding = (40 - len(title)) % 2  # Jeśli tytuł ma nieparzystą liczbę znaków

    return f"\n{COLORS['blue']}{line}\n{'=' * padding}{title}{'=' * (padding + extra_padding)}\n{line}{COLORS['reset']}\n"

def print_section_title(title):
    """Generates a smaller section title without top and bottom lines"""
    title = f" {title} "
    padding = (40 - len(title)) // 2
    extra_padding = (40 - len(title)) % 2  # Jeśli tytuł ma nieparzystą liczbę znaków

    return f"\n{COLORS['cyan']}{'=' * padding}{title}{'=' * (padding + extra_padding)}{COLORS['reset']}\n"


def check_k3s_token(token_config):
    """Sprawdza token K3s i tworzy pierwszy backup."""
    token_path = token_config.get(
        "path",
        "/var/lib/rancher/k3s/server/token",
    )
    backup_path = token_config.get(
        "backup_path",
        "/var/backups/krowa-admin/k3s-token.bak",
    )

    if not os.path.exists(token_path):
        return (
            f"{COLORS['red']}✖ K3s token is missing"
            f"{COLORS['reset']}\n"
        )

    try:
        with open(token_path, "r", encoding="utf-8") as token_file:
            token_content = token_file.read().strip()

        if len(token_content) < 20:
            return (
                f"{COLORS['yellow']}⚠ K3s token is empty or corrupted"
                f"{COLORS['reset']}\n"
            )

        if not os.path.exists(backup_path):
            backup_directory = os.path.dirname(backup_path)
            os.makedirs(backup_directory, exist_ok=True)

            shutil.copy2(token_path, backup_path)
            os.chmod(backup_path, 0o640)

            return (
                f"{COLORS['green']}✔ K3s token backup created"
                f"{COLORS['reset']}\n"
            )

        with open(backup_path, "r", encoding="utf-8") as backup_file:
            backup_content = backup_file.read().strip()

        if token_content != backup_content:
            return (
                f"{COLORS['yellow']}⚠ K3s token has changed; "
                f"backup was not overwritten{COLORS['reset']}\n"
            )

        return (
            f"{COLORS['green']}✔ K3s token matches backup"
            f"{COLORS['reset']}\n"
        )

    except (OSError, PermissionError) as error:
        return (
            f"{COLORS['red']}✖ Unable to check K3s token: "
            f"{error}{COLORS['reset']}\n"
        )


def check_service_status(service_name):
    """Sprawdza status usługi za pomocą systemctl"""
    status = os.system(f"systemctl is-active --quiet {service_name}")
    return status == 0

def get_k3s_status():
    """Pobiera status klastra K3s, jeśli działa"""
    try:
        node_status = subprocess.check_output("kubectl get nodes --no-headers", shell=True, text=True).strip()
        pod_count = subprocess.check_output("kubectl get pods -A --no-headers | wc -l", shell=True, text=True).strip()
        report = "\n"
        report += print_section_title("K3s CLUSTER STATUS")
        report += f"{COLORS['green']}Nodes:\n{node_status}\nRunning Pods: {pod_count}{COLORS['reset']}"
        return report
    except subprocess.CalledProcessError:
        report = "\n"
        report += print_section_title("K3s CLUSTER STATUS")  # Żółty nagłówek
        report += f"\n{COLORS['yellow']}⚠ K3s is running, but unable to fetch status.{COLORS['reset']}"
        return report

def get_namespace_report(namespaces_config):
    """Pobiera listę namespace’ów i rozdziela je na systemowe oraz użytkownika"""
    try:
        namespaces = subprocess.check_output("kubectl get namespaces --no-headers", shell=True, text=True).strip().split("\n")
        system_namespaces = {"default", "kube-system", "kube-public", "kube-node-lease", "metallb-system"}
        
        system_ns = []
        user_ns = []

        for ns in namespaces:
            name = ns.split()[0]
            if name in system_namespaces:
                system_ns.append(name)
            else:
                user_ns.append(name)

        report = "\n"
        report += print_section_title("K3s NAMESPACES")
        report += f"{COLORS['green']}System Namespaces:{COLORS['reset']} {', '.join(system_ns)}\n"
        report += f"{COLORS['yellow']}User Namespaces:{COLORS['reset']} {', '.join(user_ns)}\n"

        return report
    except subprocess.CalledProcessError:
        return f"\n{COLORS['yellow']}Unable to fetch namespaces.{COLORS['reset']}"


def get_docker_container_report(docker_config):
    """Sprawdza stan kontenerów wymienionych jako expected."""
    report = print_section_title("DOCKER CONTAINERS")
    expected = docker_config.get("expected", [])

    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--format",
                "{{.Names}}|{{.Status}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        return (
            report
            + f"{COLORS['yellow']}Unable to check Docker: "
            + f"{error}{COLORS['reset']}\n"
        )

    containers = {}

    for line in result.stdout.splitlines():
        name, status = line.split("|", 1)
        containers[name] = status

    for name in expected:
        status = containers.get(name)

        if status is None:
            report += (
                f"{COLORS['red']}✖ {name}: missing"
                f"{COLORS['reset']}\n"
            )
        elif "(unhealthy)" in status:
            report += (
                f"{COLORS['yellow']}⚠ {name}: {status}"
                f"{COLORS['reset']}\n"
            )
        elif status.startswith("Up"):
            report += (
                f"{COLORS['green']}✔ {name}: running"
                f"{COLORS['reset']}\n"
            )
        else:
            report += (
                f"{COLORS['red']}✖ {name}: {status}"
                f"{COLORS['reset']}\n"
            )

    return report

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

    report += f"\n\n{COLORS['cyan']}(This script is located at: /usr/local/bin/service-status.py){COLORS['reset']}"
    report += f"\n{COLORS['cyan']}(Triggered by: /etc/profile.d/service-status.sh){COLORS['reset']}\n"
    
    return report

if __name__ == "__main__":

    if services_config.get("enabled", False):
        services = services_config.get("items", [])
    else:
        services = []

    report = generate_status_report()
    print(report)


import os
import shutil
import subprocess

from formatting import COLORS, print_section_title


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

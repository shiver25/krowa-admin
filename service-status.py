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

# Lista usług do sprawdzenia
services = ["docker", "ssh", "k3s"]

TOKEN_PATH = "/var/lib/rancher/k3s/server/token"
BACKUP_PATH = "/home/pi/k3s-token-backup/token.bak"

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

def create_k3s_token_backup():
    """Tworzy backup tokena K3s z poprawnymi uprawnieniami"""
    if os.path.exists(TOKEN_PATH):
        shutil.copy2(TOKEN_PATH, BACKUP_PATH)
        os.chmod(BACKUP_PATH, 0o640)  # Prawa dostępu jak w tokenie

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


def check_k3s_token():
    """Sprawdza, czy plik tokena K3s istnieje, jest poprawny i czy nie zmienił się względem backupu"""
    
    # Sprawdzenie czy plik tokena w ogóle istnieje
    if not os.path.exists(TOKEN_PATH):
        return f"{COLORS['red']}✖ K3s token is MISSING! Possible issue after restart{COLORS['reset']}"

    try:
        with open(TOKEN_PATH, "r") as file:
            token_content = file.read().strip()
        
        # Sprawdzenie czy token jest pusty lub za krótki
        if len(token_content) < 20:  # Normalny token ma ok. 50+ znaków
            return f"{COLORS['yellow']}⚠ K3s token is EMPTY or CORRUPTED! Check file content.{COLORS['reset']}"

        # Sprawdzenie, czy mamy kopię zapasową
        if os.path.exists(BACKUP_PATH):
            with open(BACKUP_PATH, "r") as backup_file:
                backup_content = backup_file.read().strip()

            # Porównanie obecnego tokena z backupem
            if token_content != backup_content:
                return f"{COLORS['yellow']}⚠ K3s token has CHANGED! This might be unexpected.{COLORS['reset']}"
        
        # Jeśli wszystko wygląda OK, aktualizujemy backup
        shutil.copy2(TOKEN_PATH, BACKUP_PATH)
        return f"{COLORS['green']}✔ K3s token exists and matches backup{COLORS['reset']}"

    except Exception as e:
        return f"{COLORS['red']}✖ Error reading K3s token: {str(e)}{COLORS['reset']}"

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

def get_namespace_report():
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

def generate_status_report():
    """Generuje raport o statusie usług"""
    report = "\n"
    report += print_section_header("KROWA ADMIN")
    report += print_section_title("SERVICE STATUS REPORT")
    for service in services:
        status_str = f"{COLORS['green']}✔ running{COLORS['reset']}" if check_service_status(service) else f"{COLORS['red']}✖ not running{COLORS['reset']}"
        report += f"{service}: {status_str}\n"

    if check_service_status("k3s"):
        report += get_k3s_status()
    
    report += "\n" + get_namespace_report()
    report += "\n" + check_k3s_token() + "\n"
    report += f"\n\n{COLORS['cyan']}(This script is located at: /usr/local/bin/service-status.py){COLORS['reset']}"
    report += f"\n{COLORS['cyan']}(Triggered by: /etc/profile.d/service-status.sh){COLORS['reset']}\n"
    
    return report

if __name__ == "__main__":
    create_k3s_token_backup()
    report = generate_status_report()
    print(report)


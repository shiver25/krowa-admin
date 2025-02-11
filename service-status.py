#!/usr/bin/env python3

# Service Status Script
# This script is executed at login via /etc/profile.d/service-status.sh
# Located at: /usr/local/bin/service-status.py

import os
import shutil
import subprocess

# Lista usług do sprawdzenia
services = ["docker", "ssh", "k3s"]

TOKEN_PATH = "/var/lib/rancher/k3s/server/token"
BACKUP_PATH = "/home/pi/k3s-token-backup/token.bak"

def create_k3s_token_backup():
    """Tworzy backup tokena K3s z poprawnymi uprawnieniami"""
    if os.path.exists(TOKEN_PATH):
        shutil.copy2(TOKEN_PATH, BACKUP_PATH)
        os.chmod(BACKUP_PATH, 0o640)  # Prawa dostępu jak w tokenie

def check_k3s_token():
    """Sprawdza, czy plik tokena K3s istnieje, jest poprawny i czy nie zmienił się względem backupu"""
    
    # Sprawdzenie czy plik tokena w ogóle istnieje
    if not os.path.exists(TOKEN_PATH):
        return "\033[1;31m✖ K3s token is MISSING! Possible issue after restart\033[0m"

    try:
        with open(TOKEN_PATH, "r") as file:
            token_content = file.read().strip()
        
        # Sprawdzenie czy token jest pusty lub za krótki
        if len(token_content) < 20:  # Normalny token ma ok. 50+ znaków
            return "\033[1;33m⚠ K3s token is EMPTY or CORRUPTED! Check file content.\033[0m"

        # Sprawdzenie, czy mamy kopię zapasową
        if os.path.exists(BACKUP_PATH):
            with open(BACKUP_PATH, "r") as backup_file:
                backup_content = backup_file.read().strip()

            # Porównanie obecnego tokena z backupem
            if token_content != backup_content:
                return "\033[1;33m⚠ K3s token has CHANGED! This might be unexpected.\033[0m"
        
        # Jeśli wszystko wygląda OK, aktualizujemy backup
        shutil.copy2(TOKEN_PATH, BACKUP_PATH)
        return "\033[1;32m✔ K3s token exists and matches backup\033[0m"

    except Exception as e:
        return f"\033[1;31m✖ Error reading K3s token: {str(e)}\033[0m"

def check_service_status(service_name):
    """Sprawdza status usługi za pomocą systemctl"""
    status = os.system(f"systemctl is-active --quiet {service_name}")
    return status == 0

def get_k3s_status():
    """Pobiera status klastra K3s, jeśli działa"""
    try:
        node_status = subprocess.check_output("kubectl get nodes --no-headers", shell=True, text=True).strip()
        pod_count = subprocess.check_output("kubectl get pods -A --no-headers | wc -l", shell=True, text=True).strip()
        return f"\n\033[1;34m===== K3s CLUSTER STATUS =====\033[0m\n\033[1;32mNodes:\n{node_status}\nRunning Pods: {pod_count}\033[0m"
    except subprocess.CalledProcessError:
        return "\n\033[1;33mK3s is running, but unable to fetch status.\033[0m"

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

        report = "\n\033[1;34m===== K3s NAMESPACES =====\033[0m\n"
        report += f"\033[1;32mSystem Namespaces:\033[0m {', '.join(system_ns)}\n"
        report += f"\033[1;33mUser Namespaces:\033[0m {', '.join(user_ns)}\n"

        return report
    except subprocess.CalledProcessError:
        return "\n\033[1;33mUnable to fetch namespaces.\033[0m"

def generate_status_report():
    """Generuje raport o statusie usług"""
    report = "\n\033[1;34m===== SERVICE STATUS REPORT =====\033[0m\n"
    for service in services:
        status_str = "\033[1;32m✔ running\033[0m" if check_service_status(service) else "\033[1;31m✖ not running\033[0m"
        report += f"{service}: {status_str}\n"

    if check_service_status("k3s"):
        report += get_k3s_status()
    
    report += "\n" + get_namespace_report()
    report += "\n" + check_k3s_token() + "\n"
    report += "\n\n\033[1;36m(This script is located at: /usr/local/bin/service-status.py)\033[0m"
    report += "\n\033[1;36m(Triggered by: /etc/profile.d/service-status.sh)\033[0m"
    print(report)

if __name__ == "__main__":
    create_k3s_token_backup()
    generate_status_report()


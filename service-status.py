#!/usr/bin/env python3

# Service Status Script
# This script is executed at login via /etc/profile.d/service-status.sh
# Located at: /usr/local/bin/service-status.py

import os
import subprocess

# Lista usług do sprawdzenia
services = ["docker", "ssh", "k3s"]

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
    report += "\n\n\033[1;36m(This script is located at: /usr/local/bin/service-status.py)\033[0m"
    report += "\n\033[1;36m(Triggered by: /etc/profile.d/service-status.sh)\033[0m"

    print(report)

if __name__ == "__main__":
    generate_status_report()


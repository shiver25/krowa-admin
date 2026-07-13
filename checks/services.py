import os
os.system("")

def check_service_status(service_name):
    """Sprawdza status usługi za pomocą systemctl"""
    status = os.system(f"systemctl is-active --quiet {service_name}")
    return status == 0
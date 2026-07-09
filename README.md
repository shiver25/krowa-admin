# 🐄 Krowa Admin - Service Status

## 📌 About
Krowa Admin is a simple yet effective script that **displays the status of key services** (`docker`, `ssh`, `k3s`) and provides a **summary of the K3s cluster** every time a user logs in.  

## 🚀 Installation
```bash
git clone https://github.com/shiver25/krowa-admin.git
cd krowa-admin
sudo cp service-status.py /usr/local/bin/
sudo chmod +x /usr/local/bin/service-status.py
sudo cp service-status.sh /etc/profile.d/
sudo chmod +x /etc/profile.d/service-status.sh
```

## 🎯 Features

✅ Shows system service status (docker, ssh, k3s)
✅ Displays K3s cluster info (nodes & running pods)
✅ Automatically categorizes system and user namespaces
✅ Color-coded and readable output
✅ Runs automatically on login

## 🔹 K3s Token Backup & Validation
Krowa Admin automatically checks and backs up the K3s token file to help diagnose issues after a system restart.

### ✅ How does it work?
1. The script verifies whether the token file `/var/lib/rancher/k3s/server/token` exists and if the `pi` user has access to it.
2. If the token file exists and is valid, the script compares it to the backup stored in **`/home/pi/k3s-token-backup/`**.
3. If the token has changed since the last backup, a warning is displayed.
4. If the token is missing or empty, the user receives a clear alert.

### 📌 Where is the token backup stored?
The backup file is saved at:
```bash
/home/pi/k3s-token-backup/token.bak
```

This allows the `pi` user to access it without requiring root privileges.

### ⚠ What to do if `Permission Denied` occurs?
If the script reports **"K3s token is MISSING!"**, but the file actually exists:

1. **Check if the `pi` user has access to the token file:**  
   ```bash
   cat /var/lib/rancher/k3s/server/token
   ```
2. **If you see Permission denied, try:**
    ```bash
    newgrp k3s
    ```
3. **Verify that /var/lib/rancher/k3s/server/ has the correct permissions:**
    ```bash
    ls -ld /var/lib/rancher/k3s/server
    ```
4. **If the group k3s does not have read access, fix it with:**
    ```bash
    sudo chmod 750 /var/lib/rancher/k3s/server
    ```
5. **If the issue persists, log out and log back in:**
    ```bash
    logout
    ssh pi@raspberrypi
    ```
## 📸 Example Output

```bash
===== SERVICE STATUS REPORT =====
docker: ✔ running
ssh: ✔ running
k3s: ✔ running

===== K3S CLUSTER STATUS =====
Nodes:
raspberrypi   Ready   control-plane,master   235d   v1.31.5+k3s1
Running Pods: 24

===== K3S NAMESPACES =====
System Namespaces: default, kube-node-lease, kube-public, kube-system, metallb-system
User Namespaces: kubernetes-dashboard, logos-dev, my-app-namespace, playground, test-docker-ci

✔ K3s token exists and matches backup


(This script is located at: /usr/local/bin/service-status.py)
(Triggered by: /etc/profile.d/service-status.sh)
```

## 🔧 How It Works

1. The script checks if the required services are running (docker, ssh, k3s).
2. If k3s is active, it retrieves:
    - The status of cluster nodes (kubectl get nodes)
    - The number of running pods (kubectl get pods -A | wc -l)
3. It separates system namespaces (default, kube-system, kube-public, etc.) from user-created namespaces.
4. The output is formatted in colors for clarity.
5. Runs automatically on login via /etc/profile.d/service-status.sh.

## 🎸 Author

🐄 Krowa Admin
🚀 GitHub: shiver25
📜 License

Projekt jest rozwijany i utrzymywany przez firmę **[LOGOS](https://logos.net.pl)**. 
Oferujemy profesjonalne wsparcie, administrację serwerami Linux oraz optymalizację infrastruktury webowej.

MIT License – Free to use, modify, and share. 🎉

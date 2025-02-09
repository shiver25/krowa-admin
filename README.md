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

MIT License – Free to use, modify, and share. 🎉

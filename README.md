# 🐄 Krowa Admin - Service Status

## 📌 About
Krowa Admin is a simple yet effective script that **displays the status of key services** (`docker`, `ssh`, `k3s`) and provides a **summary of the K3s cluster** every time a user logs in.  

## 🚀 Installation
```bash
git clone https://github.com/YourGitHubUsername/k3s-status.git
cd k3s-status
sudo cp service-status.py /usr/local/bin/
sudo chmod +x /usr/local/bin/service-status.py
sudo cp service-status.sh /etc/profile.d/
sudo chmod +x /etc/profile.d/service-status.sh


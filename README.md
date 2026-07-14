# Krowa Admin

Krowa Admin is a configurable server status report for Linux. It can check
systemd services, expected Docker containers, and selected K3s resources. The
same installation can be used on different hosts while each host enables only
the checks it needs in its local YAML configuration.

The report can be run manually with `krowa-admin`. Packages also install a
small `/etc/profile.d/` script that displays the report in interactive login
shells.

## Features

- Configurable systemd service checks.
- Optional uptime, load average, memory, swap, and disk usage reports.
- Expected Docker container checks, including missing, stopped, and unhealthy
  containers.
- Optional K3s node, running pod, and namespace reports.
- Optional K3s token validation against a local backup.
- Colored terminal output.
- Native DEB and RPM packages generated from one nFPM configuration.

All checks are disabled in the example configuration by default.

## Installation

Download the package for your distribution from the GitHub release.

Raspberry Pi OS, Debian, and related distributions:

```bash
sudo apt-get install ./krowa-admin_*_all.deb
```

Fedora and related RPM-based distributions:

```bash
sudo dnf install ./krowa-admin-*.noarch.rpm
```

The packages install Python and PyYAML through distribution dependencies.
Docker and `kubectl` are optional and are only needed when their corresponding
checks are enabled.

## Configuration

The host-specific configuration is stored at:

```text
/etc/krowa-admin/config.yaml
```

Example:

```yaml
checks:
  system_resources:
    enabled: true

    uptime:
      enabled: true

    load:
      enabled: true

    memory:
      enabled: true

    disk:
      enabled: true
      warning_percent: 80
      critical_percent: 90
      paths:
        - /
        - /home

  services:
    enabled: true
    items:
      - docker
      - ssh

  docker_containers:
    enabled: true
    expected:
      - example-frontend
      - example-backend

  k3s:
    enabled: false

    token:
      enabled: false
      path: /var/lib/rancher/k3s/server/token
      backup_path: /var/backups/krowa-admin/k3s-token.bak

    namespaces:
      enabled: true
      system:
        - default
        - kube-system
        - kube-public
        - kube-node-lease
        - metallb-system
```

The `services` section provides a general systemd status list. Specialized
sections provide additional diagnostics. For example, `k3s` may be listed in
`services` while `checks.k3s.enabled` controls the detailed cluster checks.

The `system_resources` section can display uptime, load averages normalized by
the number of CPUs, memory and active swap usage, and disk usage for configured
paths. Disk usage is yellow at `warning_percent` and red at
`critical_percent`. If multiple paths are located on the same filesystem, they
may report the same capacity and usage values.

The package treats `/etc/krowa-admin/config.yaml` as a configuration file, so
local changes are preserved during upgrades.

## Usage

Run a fresh report manually:

```bash
krowa-admin
```

The package installs `/etc/profile.d/krowa-admin.sh`, which runs the same
command for interactive login shells. To disable the automatic login report
without disabling the command itself, remove or locally disable that profile
script.

Installed files:

```text
/usr/bin/krowa-admin
/usr/lib/krowa-admin/
/etc/krowa-admin/config.yaml
/etc/profile.d/krowa-admin.sh
```

## K3s Token Check

The token check is disabled by default. When enabled, Krowa Admin:

1. Verifies that the configured token exists and is not empty.
2. Creates the first backup if no backup exists.
3. Compares later token values with that backup.
4. Warns about a change without overwriting the existing backup.

The user running Krowa Admin must be able to read the token and write to the
configured backup directory. Grant only the minimum permissions required and
do not make the K3s token publicly readable. The report never prints the token
contents.

## Building Packages

Docker is the only build prerequisite. The build script runs the pinned nFPM
image and creates both formats in `dist/`:

```bash
./build_and_test/build_in_docker.sh
```

Set another package version with an environment variable:

```bash
VERSION=1.2.3 ./build_and_test/build_in_docker.sh
```

The scripts can be called from any working directory.

## Testing Packages

The tests install each package and its dependencies in a clean distribution
container, compile all Python modules, verify installed files, and execute the
`krowa-admin` command:

```bash
./build_and_test/deb_test_in_docker.sh
./build_and_test/rpm_test_in_docker.sh
```

The current test images are Debian 13 and Fedora 44. Package signing and an
APT/DNF repository are not part of the initial release process.

## Project

Krowa Admin is developed by [LOGOS](https://logos.net.pl). The source is
available at [github.com/shiver25/krowa-admin](https://github.com/shiver25/krowa-admin).

License: MIT.

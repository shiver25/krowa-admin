import os
import shutil
import subprocess

from formatting import COLORS


def get_uptime_report():
    try:
        result = subprocess.run(
            [
                "uptime",
                "-p"
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )

        uptime = result.stdout.strip()

        return (
            f"Uptime: {COLORS['green']}"
            f"{uptime}{COLORS['reset']}\n"
        )
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ) as error:
        return (
            f"Uptime: {COLORS['yellow']}unavailable: "
            f"{error}{COLORS['reset']}\n"
        )


def get_load_report():
    try:
        load_1, load_5, load_15 = os.getloadavg()
        cpu_count = os.cpu_count() or 1
        load_per_cpu = load_1 / cpu_count

        if load_per_cpu >= 1:
            color = COLORS["red"]
        elif load_per_cpu >= 0.7:
            color = COLORS["yellow"]
        else:
            color = COLORS["green"]

        return (
            f"Load average: {color}"
            f"{load_1:.2f} / {load_5:.2f} / {load_15:.2f}"
            f"{COLORS['reset']}\n"
            f"Load per CPU (1 min): {color}"
            f"{load_per_cpu:.2f} ({cpu_count} CPUs)"
            f"{COLORS['reset']}\n\n"
        )

    except OSError as error:
        return (
            f"Load average: {COLORS['yellow']}"
            f"unavailable: {error}"
            f"{COLORS['reset']}\n"
        )


def format_bytes(value):
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    size = float(value)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"

        size /= 1024


def get_memory_report():
    try:
        result = subprocess.run(
            ["free", "--bytes"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
            env={
                **os.environ,
                "LC_ALL": "C",
            },
        )

        rows = {}

        for line in result.stdout.splitlines():
            columns = line.split()

            if not columns:
                continue

            row_name = columns[0].rstrip(":").lower()

            if row_name in ("mem", "swap"):
                rows[row_name] = [
                    int(value)
                    for value in columns[1:]
                ]

        memory = rows.get("mem")

        if memory is None or len(memory) < 6:
            raise ValueError("unexpected output from free")

        memory_total = memory[0]
        memory_used = memory[1]
        memory_available = memory[5]

        memory_percent = (
            memory_used / memory_total * 100
            if memory_total
            else 0
        )

        report = (
            f"Memory: {COLORS['green']}"
            f"{format_bytes(memory_used)} / "
            f"{format_bytes(memory_total)} "
            f"({memory_percent:.0f}% used)"
            f"{COLORS['reset']}\n"
            f"Available: {COLORS['green']}"
            f"{format_bytes(memory_available)}"
            f"{COLORS['reset']}\n"
        )

        swap = rows.get("swap")

        if swap is not None and len(swap) >= 2:
            swap_total = swap[0]
            swap_used = swap[1]

            if swap_used > 0:
                swap_percent = (
                    swap_used / swap_total * 100
                    if swap_total
                    else 0
                )

                report += (
                    f"Swap: {COLORS['yellow']}"
                    f"{format_bytes(swap_used)} / "
                    f"{format_bytes(swap_total)} "
                    f"({swap_percent:.0f}% used)"
                    f"{COLORS['reset']}\n"
                )

        return report

    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        ValueError,
    ) as error:
        return (
            f"Memory: {COLORS['yellow']}"
            f"unavailable: {error}"
            f"{COLORS['reset']}\n"
        )


def get_disk_report(disk_settings):
    paths = disk_settings.get("paths", ["/"])
    warning_percent = disk_settings.get(
        "warning_percent",
        80,
    )
    critical_percent = disk_settings.get(
        "critical_percent",
        90,
    )

    disk_reports = []

    for path in paths:
        try:
            total, used, free = shutil.disk_usage(path)

            used_percent = (
                used / total * 100
                if total
                else 0
            )

            if used_percent >= critical_percent:
                color = COLORS["red"]
            elif used_percent >= warning_percent:
                color = COLORS["yellow"]
            else:
                color = COLORS["green"]

            disk_reports.append(
                f"Disk {path}: {color}"
                f"{format_bytes(used)} / "
                f"{format_bytes(total)} "
                f"({used_percent:.0f}% used)"
                f"{COLORS['reset']}\n"
                f"Available: {color}"
                f"{format_bytes(free)}"
                f"{COLORS['reset']}"
            )

        except OSError as error:
            disk_reports.append(
                f"Disk {path}: {COLORS['yellow']}"
                f"unavailable: {error}"
                f"{COLORS['reset']}"
            )

    return "\n\n".join(disk_reports) + "\n"

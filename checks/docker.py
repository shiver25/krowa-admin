import subprocess
from formatting import COLORS, print_section_title


def get_docker_container_report(docker_config):
    """Sprawdza stan kontenerów wymienionych jako expected."""
    report = print_section_title("DOCKER CONTAINERS")
    expected = docker_config.get("expected", [])

    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--format",
                "{{.Names}}|{{.Status}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        return (
            report
            + f"{COLORS['yellow']}Unable to check Docker: "
            + f"{error}{COLORS['reset']}\n"
        )

    containers = {}

    for line in result.stdout.splitlines():
        name, status = line.split("|", 1)
        containers[name] = status

    for name in expected:
        status = containers.get(name)

        if status is None:
            report += (
                f"{COLORS['red']}✖ {name}: missing"
                f"{COLORS['reset']}\n"
            )
        elif "(unhealthy)" in status:
            report += (
                f"{COLORS['yellow']}⚠ {name}: {status}"
                f"{COLORS['reset']}\n"
            )
        elif status.startswith("Up"):
            report += (
                f"{COLORS['green']}✔ {name}: running"
                f"{COLORS['reset']}\n"
            )
        else:
            report += (
                f"{COLORS['red']}✖ {name}: {status}"
                f"{COLORS['reset']}\n"
            )

    return report

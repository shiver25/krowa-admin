import subprocess
from formatting import COLORS, print_section_title


def get_docker_container_statuses(docker_config):
    """Zwraca stany kontenerów wymienionych jako expected."""

    expected = docker_config.get("expected", [])

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


    containers = {}

    for line in result.stdout.splitlines():
        name, status = line.split("|", 1)
        containers[name] = status

    statuses = []

    for name in expected:
        docker_status = containers.get(name)

        if docker_status is None:
            state = "missing"
        elif "(unhealthy)" in docker_status:
            state = "unhealthy"
        elif docker_status.startswith("Up"):
            state = "running"
        else:
            state = "stopped"

        statuses.append(
            {
                "name": name,
                "state": state,
                "details": docker_status,
            }
        )

    return statuses

def format_docker_container_status(container, name_width):
    name = container["name"]
    state = container["state"]
    details = container.get("details")

    if state == "running":
        return (
            f"{COLORS['green']}✔ "
            f"{name:<{name_width}} "
            f"{details or 'running'}"
            f"{COLORS['reset']}\n"
        )

    if state == "unhealthy":
        return (
            f"{COLORS['yellow']}⚠ "
            f"{name:<{name_width}} "
            f"{details or 'unhealthy'}"
            f"{COLORS['reset']}\n"
        )

    if state == "missing":
        return (
            f"{COLORS['red']}✖ "
            f"{name:<{name_width}} "
            f"missing"
            f"{COLORS['reset']}\n"
        )

    return (
        f"{COLORS['red']}✖ "
        f"{name:<{name_width}} "
        f"{details or 'stopped'}"
        f"{COLORS['reset']}\n"
    )


def format_docker_summary(statuses, problems):
    counts = {
        "running": 0,
        "stopped": 0,
        "unhealthy": 0,
        "missing": 0,
    }

    for container in statuses:
        counts[container["state"]] += 1

    report = (
        f"Containers: {counts['running']} running, "
        f"{counts['stopped']} stopped, "
        f"{counts['unhealthy']} unhealthy, "
        f"{counts['missing']} missing\n"
    )

    if not problems:
        return (
            report
            + f"{COLORS['green']}✔ All expected containers are running"
            + f"{COLORS['reset']}\n"
        )

    name_width = max(len(container["name"]) for container in problems)
    report += "\n"

    for container in problems:
        report += format_docker_container_status(container, name_width)

    return report


def format_docker_container_report(statuses, mode="full"):
    report = print_section_title("DOCKER CONTAINERS")

    if not statuses:
        return report + "No expected containers configured\n"

    name_width = max(len(container["name"]) for container in statuses)

    problems = [
        container
        for container in statuses
        if container["state"] != "running"
    ]

    if mode == "summary":
        return report + format_docker_summary(statuses, problems)

    containers_to_show = problems if mode == "problems" else statuses

    if mode == "problems" and not containers_to_show:
        return (
            report
            + f"{COLORS['green']}✔ No Docker container problems detected"
            + f"{COLORS['reset']}\n"
        )

    for container in containers_to_show:
        report += format_docker_container_status(
            container,
            name_width=name_width,
        )

    return report


def get_docker_container_report(docker_config, mode="full"):
    try:
        statuses = get_docker_container_statuses(docker_config)
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        return (
            print_section_title("DOCKER CONTAINERS")
            + f"{COLORS['yellow']}Unable to check Docker: "
            + f"{error}{COLORS['reset']}\n"
        )

    return format_docker_container_report(
        statuses,
        mode=mode,
    )

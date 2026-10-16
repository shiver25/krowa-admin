from pathlib import Path

from formatting import print_section_title


DEFAULT_DOCUMENTATION_CONFIG = Path("/etc/krowa-admin/docs.conf")


def load_documentation_entries(path=DEFAULT_DOCUMENTATION_CONFIG):
    """Return configured documentation entries whose target files exist."""
    entries = []

    try:
        with Path(path).open("r", encoding="utf-8") as config_file:
            for raw_line in config_file:
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                if line.count("|") != 1:
                    continue

                name, documentation_path = (
                    part.strip() for part in line.split("|", 1)
                )

                if not name or not documentation_path:
                    continue

                target = Path(documentation_path)
                if not target.is_absolute():
                    continue

                try:
                    if not target.is_file():
                        continue
                except OSError:
                    continue

                entries.append((name, str(target)))
    except (OSError, UnicodeError):
        return entries

    return entries


def get_documentation_report(path=DEFAULT_DOCUMENTATION_CONFIG):
    entries = load_documentation_entries(path)

    if not entries:
        return ""

    name_width = max(len(name) for name, _ in entries)
    report = print_section_title("DOCUMENTATION")

    for name, documentation_path in entries:
        report += f"{name:<{name_width}}  {documentation_path}\n"

    return report

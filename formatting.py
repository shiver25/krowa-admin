# ANSI Escape Codes - Colors
COLORS = {
    "reset": "\033[0m",
    "red": "\033[1;31m",
    "green": "\033[1;32m",
    "yellow": "\033[1;33m",
    "blue": "\033[1;34m",
    "magenta": "\033[1;35m",
    "cyan": "\033[1;36m",
    "white": "\033[1;37m",
}


def print_section_header(title):
    """Generuje nagłówek sekcji w raporcie"""
    line = "=" * 40
    title = f" {title} "
    padding = (40 - len(title)) // 2
    extra_padding = (40 - len(title)) % 2  # Jeśli tytuł ma nieparzystą liczbę znaków

    return f"\n{COLORS['blue']}{line}\n{'=' * padding}{title}{'=' * (padding + extra_padding)}\n{line}{COLORS['reset']}\n"

def print_section_title(title):
    """Generates a smaller section title without top and bottom lines"""
    title = f" {title} "
    padding = (40 - len(title)) // 2
    extra_padding = (40 - len(title)) % 2  # Jeśli tytuł ma nieparzystą liczbę znaków

    return f"\n{COLORS['cyan']}{'=' * padding}{title}{'=' * (padding + extra_padding)}{COLORS['reset']}\n"
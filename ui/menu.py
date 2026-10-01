from rich.prompt import Prompt
from core import config
from ui import widgets

MAIN_ITEMS = [
    ("1", "Device Info"),
    ("2", "Battery & Power"),
    ("3", "Packages"),
    ("4", "Network"),
    ("5", "Files"),
    ("6", "Capture"),
    ("7", "Logcat"),
    ("8", "Switch Device"),
    ("9", "Apk Analyzer"),
    ("0", "Exit"),
]


def main_menu():
    lines = "\n".join(f"[{config.ACCENT}][{k}][/] {v}" for k, v in MAIN_ITEMS)
    widgets.panel(lines, title=f"[bold {config.PRIMARY}]{config.APP_NAME}[/]")
    return Prompt.ask(f"[{config.PRIMARY}]shiftedmind[/] ❯", default="0")

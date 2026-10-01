from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from core import config

console = Console()


def table(title, columns, rows, color=config.ACCENT):
    t = Table(title=title, border_style=color, title_style=f"bold {color}")
    for c in columns:
        t.add_column(c, style=color)
    for r in rows:
        t.add_row(*[str(x) for x in r])
    console.print(t)


def kv(title, data, color=config.ACCENT):
    t = Table(title=title, border_style=color, show_header=False)
    t.add_column("Key", style=f"bold {color}")
    t.add_column("Value")
    for k, v in data.items():
        t.add_row(str(k), str(v))
    console.print(t)


def panel(body, title=None, color=config.PRIMARY):
    console.print(Panel(body, title=title, border_style=color))


def ok(msg):    console.print(f"[{config.OK}]✓ {msg}[/]")
def err(msg):   console.print(f"[{config.DANGER}]✗ {msg}[/]")
def info(msg):  console.print(f"[{config.ACCENT}]» {msg}[/]")


def ask(prompt, default=None):
    return Prompt.ask(f"[{config.PRIMARY}]{prompt}[/]", default=default)


def confirm(prompt):
    return Confirm.ask(f"[{config.PRIMARY}]{prompt}[/]")


def code(text, lang="text"):
    console.print(Syntax(text, lang, theme="monokai", line_numbers=False))

from rich.console import Console
from rich.align import Align
from rich.text import Text
from core import config

console = Console()

BANNER = r"""
   ███████╗██╗  ██╗██╗███████╗████████╗███████╗██████╗
   ██╔════╝██║  ██║██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗
   ███████╗███████║██║█████╗     ██║   █████╗  ██║  ██║
   ╚════██║██╔══██║██║██╔══╝     ██║   ██╔══╝  ██║  ██║
   ███████║██║  ██║██║██║        ██║   ███████╗██████╔╝
   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝   ╚══════╝╚═════╝
              M   I   N   D
"""


def show():
    console.print(Align.center(Text(BANNER, style=f"bold {config.PRIMARY}")))
    console.print(Align.center(
        Text(f"v{config.VERSION}  •  {config.TAGLINE}", style=config.DIM)
    ))
    console.print()

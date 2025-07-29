from typing import List, TYPE_CHECKING
from rich import print
from rich.panel import Panel

if TYPE_CHECKING:
    from game.player import Player


def h1(title: str):
    """打印带有格式的标题"""
    print(Panel(title, title_align="left", style="bold blue"))


def h2(title: str):
    """打印带有格式的副标题"""
    print(Panel(title, title_align="left", style="bold green"))


def prompt_for_choice(
    player: "Player",
    prompt_text: str,
    valid_choices: List[str],
    allow_skip: bool = False,
) -> str:
    """根据玩家类型提示选择。"""
    if player.is_human:
        return player.call_human_response(prompt_text, valid_choices, allow_skip)
    else:
        return player.call_ai_response(prompt_text, valid_choices)

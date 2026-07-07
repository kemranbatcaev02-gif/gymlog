"""Переиспользуемые виджеты."""
import customtkinter as ctk
from .theme import fonts


class Card(ctk.CTkFrame):
    """Карточка с фоном и скруглением."""
    def __init__(self, master, palette, **kwargs):
        kwargs.setdefault("fg_color", palette["card"])
        kwargs.setdefault("corner_radius", 14)
        super().__init__(master, **kwargs)


class StatCard(Card):
    """Карточка-метрика: большое число + подпись."""
    def __init__(self, master, palette, accent, title, value, unit=""):
        super().__init__(master, palette)
        f = fonts()
        ctk.CTkLabel(self, text=title, font=f["small"],
                     text_color=palette["text_dim"]).pack(anchor="w", padx=16, pady=(14, 0))
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(anchor="w", padx=16, pady=(2, 14))
        ctk.CTkLabel(row, text=str(value), font=f["stat"],
                     text_color=accent["main"]).pack(side="left")
        if unit:
            ctk.CTkLabel(row, text=f" {unit}", font=f["body"],
                         text_color=palette["text_dim"]).pack(side="left", pady=(10, 0))


def page_title(master, palette, text, subtitle=None):
    f = fonts()
    ctk.CTkLabel(master, text=text, font=f["h1"],
                 text_color=palette["text"]).pack(anchor="w", padx=28, pady=(24, 0))
    if subtitle:
        ctk.CTkLabel(master, text=subtitle, font=f["body"],
                     text_color=palette["text_dim"]).pack(anchor="w", padx=28, pady=(2, 0))

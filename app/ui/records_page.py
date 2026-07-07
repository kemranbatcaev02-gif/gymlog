"""Личные рекорды: лучший подход и расчётный 1ПМ по каждому упражнению."""
import customtkinter as ctk
from .theme import fonts
from .widgets import Card, page_title


class RecordsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        f = fonts()
        a = app.config.accent

        page_title(self, p, "🏆 Рекорды",
                   "1ПМ считается по формуле Эпли: вес × (1 + повторы / 30)")

        records = app.db.get_personal_records()
        if not records:
            ctk.CTkLabel(self, text="Рекорды появятся после первых тренировок 💪",
                         font=f["body"], text_color=p["text_dim"]).pack(pady=40)
            return

        u = app.config.units
        top = max(records.values(), key=lambda r: r["est_1rm"])

        for ex, r in records.items():
            card = Card(self, p)
            card.pack(fill="x", padx=24, pady=4)
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=12)

            crown = " 👑" if r is top else ""
            ctk.CTkLabel(row, text=ex + crown, font=f["h3"],
                         text_color=p["text"]).pack(side="left")

            right = ctk.CTkFrame(row, fg_color="transparent")
            right.pack(side="right")
            ctk.CTkLabel(right, text=f'{r["weight"]:g} {u} × {r["reps"]}',
                         font=f["body"], text_color=p["text_dim"]).pack(anchor="e")
            ctk.CTkLabel(right, text=f'1ПМ ≈ {r["est_1rm"]:g} {u}  ·  {r["date"]}',
                         font=f["small"], text_color=a["main"]).pack(anchor="e")

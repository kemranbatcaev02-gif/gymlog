"""Дашборд: приветствие, метрики, последние записи."""
from datetime import datetime
import customtkinter as ctk
from .theme import fonts
from .widgets import Card, StatCard


GOAL_TIPS = {
    "Сила": "Держи 3–6 повторов с большим весом и отдыхай 2–3 минуты между подходами.",
    "Масса": "Рабочая зона 8–12 повторов, следи за прогрессией веса от недели к неделе.",
    "Похудение": "Больше объёма и кардио, отдых короче — 45–60 секунд.",
    "Выносливость": "15+ повторов, суперсеты и круговые — твои лучшие друзья.",
}


class DashboardFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        self.app = app
        f = fonts()
        a = app.config.accent
        stats = app.db.get_stats()
        name = app.config.profile["name"] or "чемпион"

        hour = datetime.now().hour
        hello = "Доброе утро" if 5 <= hour < 12 else "Добрый день" if hour < 18 else "Добрый вечер"

        ctk.CTkLabel(self, text=f"{hello}, {name}! 👋", font=f["h1"],
                     text_color=p["text"]).pack(anchor="w", padx=28, pady=(24, 0))
        ctk.CTkLabel(self, text=GOAL_TIPS.get(app.config.profile["goal"], ""),
                     font=f["body"], text_color=p["text_dim"],
                     wraplength=700, justify="left").pack(anchor="w", padx=28, pady=(4, 18))

        # Метрики
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=24)
        for i in range(4):
            grid.grid_columnconfigure(i, weight=1, uniform="stats")

        u = app.config.units
        cards = [
            ("Серия дней", stats["streak"], "🔥"),
            ("Тренировок за неделю", stats["workouts_this_week"], ""),
            ("Общий тоннаж", self._fmt_volume(stats["total_volume"]), u),
            ("Всего записей", stats["total_entries"], ""),
        ]
        for i, (title, value, unit) in enumerate(cards):
            StatCard(grid, p, a, title, value, unit).grid(
                row=0, column=i, padx=4, sticky="nsew")

        # Последние тренировки
        ctk.CTkLabel(self, text="Последние записи", font=f["h2"],
                     text_color=p["text"]).pack(anchor="w", padx=28, pady=(26, 8))

        recent = app.db.get_workouts(limit=8)
        if not recent:
            empty = Card(self, p)
            empty.pack(fill="x", padx=24)
            ctk.CTkLabel(empty, text="Пока пусто. Жми «➕ Тренировка» и добавь первый подход!",
                         font=f["body"], text_color=p["text_dim"]).pack(padx=20, pady=24)
        else:
            for r in recent:
                self._entry_row(r, p, a, f)

    def _fmt_volume(self, v: float) -> str:
        if v >= 1000:
            return f"{v / 1000:.1f}т".replace("т", " т")
        return f"{v:.0f}"

    def _entry_row(self, r, p, a, f):
        card = Card(self, p)
        card.pack(fill="x", padx=24, pady=3)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(row, text=r["exercise"], font=f["h3"],
                     text_color=p["text"]).pack(side="left")
        u = self.app.config.units
        detail = f'{r["weight"]:g} {u} × {r["reps"]} × {r["sets"]}'
        ctk.CTkLabel(row, text=detail, font=f["body"],
                     text_color=a["main"]).pack(side="left", padx=14)
        ctk.CTkLabel(row, text=r["date"], font=f["small"],
                     text_color=p["text_dim"]).pack(side="right")

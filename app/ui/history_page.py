"""История: фильтр по упражнению и периоду, удаление записей."""
from datetime import datetime, timedelta
import customtkinter as ctk
from .theme import fonts
from .widgets import Card, page_title

PERIODS = {"Всё время": None, "Неделя": 7, "Месяц": 30, "3 месяца": 90}


class HistoryFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        self.app = app
        self.p = p
        self.f = fonts()
        self.a = app.config.accent

        page_title(self, p, "📜 История", "Все твои записи")

        # Фильтры
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=24, pady=(14, 6))

        exercises = ["Все упражнения"] + app.db.get_exercises_used()
        self.ex_menu = ctk.CTkOptionMenu(bar, values=exercises, height=36,
                                         fg_color=p["card"], button_color=self.a["main"],
                                         button_hover_color=self.a["hover"],
                                         font=self.f["body"], command=lambda _: self._refresh())
        self.ex_menu.pack(side="left", padx=(0, 8))

        self.period_menu = ctk.CTkOptionMenu(bar, values=list(PERIODS), height=36,
                                             fg_color=p["card"], button_color=self.a["main"],
                                             button_hover_color=self.a["hover"],
                                             font=self.f["body"], command=lambda _: self._refresh())
        self.period_menu.pack(side="left")

        self.count_lbl = ctk.CTkLabel(bar, text="", font=self.f["small"],
                                      text_color=p["text_dim"])
        self.count_lbl.pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=p["bg"])
        self.list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self._refresh()

    def _refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        ex = self.ex_menu.get()
        ex = None if ex == "Все упражнения" else ex
        days = PERIODS[self.period_menu.get()]
        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d") if days else None

        rows = self.app.db.get_workouts(exercise=ex, date_from=date_from)
        self.count_lbl.configure(text=f"Записей: {len(rows)}")

        if not rows:
            ctk.CTkLabel(self.list_frame, text="Ничего не нашлось по этим фильтрам",
                         font=self.f["body"], text_color=self.p["text_dim"]).pack(pady=30)
            return

        last_date = None
        for r in rows:
            if r["date"] != last_date:
                last_date = r["date"]
                ctk.CTkLabel(self.list_frame, text=self._pretty_date(r["date"]),
                             font=self.f["h3"], text_color=self.p["text_dim"]
                             ).pack(anchor="w", padx=10, pady=(14, 4))
            self._row(r)

    def _pretty_date(self, iso: str) -> str:
        months = ["января", "февраля", "марта", "апреля", "мая", "июня",
                  "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        d = datetime.strptime(iso, "%Y-%m-%d")
        return f"{d.day} {months[d.month - 1]} {d.year}"

    def _row(self, r):
        card = Card(self.list_frame, self.p)
        card.pack(fill="x", padx=8, pady=3)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=8)

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        top = ctk.CTkFrame(left, fg_color="transparent")
        top.pack(anchor="w")
        ctk.CTkLabel(top, text=r["exercise"], font=self.f["h3"],
                     text_color=self.p["text"]).pack(side="left")
        u = self.app.config.units
        detail = f'  {r["weight"]:g} {u} × {r["reps"]} повт × {r["sets"]} подх'
        if r["rpe"]:
            detail += f'  ·  RPE {r["rpe"]}'
        ctk.CTkLabel(top, text=detail, font=self.f["body"],
                     text_color=self.a["main"]).pack(side="left")

        if r["notes"]:
            ctk.CTkLabel(left, text=r["notes"], font=self.f["small"],
                         text_color=self.p["text_dim"], wraplength=560,
                         justify="left").pack(anchor="w")

        ctk.CTkButton(row, text="✕", width=32, height=32, corner_radius=8,
                      fg_color="transparent", hover_color=self.p["danger"],
                      text_color=self.p["text_dim"],
                      command=lambda i=r["id"]: self._delete(i)).pack(side="right")

    def _delete(self, workout_id):
        self.app.db.delete_workout(workout_id)
        self._refresh()

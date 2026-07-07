"""Добавление тренировки: выбор упражнения из библиотеки, ввод подходов."""
import json
from datetime import datetime
from pathlib import Path
import customtkinter as ctk
from .theme import fonts
from .widgets import Card, page_title

EXERCISES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "exercises.json"


def load_exercise_library() -> dict:
    try:
        return json.loads(EXERCISES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


class WorkoutFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        self.app = app
        self.p = p
        self.f = fonts()
        self.a = app.config.accent

        page_title(self, p, "➕ Новая тренировка",
                   "Выбери упражнение и запиши подход")

        library = load_exercise_library()
        card = Card(self, p)
        card.pack(fill="x", padx=24, pady=18)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=22)

        # Группа мышц + упражнение
        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=4)
        row1.grid_columnconfigure((0, 1), weight=1)

        self.groups = ["Все"] + list(library.keys())
        self.library = library
        self.group_menu = ctk.CTkOptionMenu(
            row1, values=self.groups, height=40, font=self.f["body"],
            fg_color=p["card_2"], button_color=self.a["main"],
            button_hover_color=self.a["hover"], command=self._on_group_change)
        self.group_menu.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.exercise_combo = ctk.CTkComboBox(
            row1, values=self._exercises_for("Все"), height=40, font=self.f["body"],
            fg_color=p["card_2"], button_color=self.a["main"],
            button_hover_color=self.a["hover"])
        self.exercise_combo.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.exercise_combo.set("")

        ctk.CTkLabel(inner, text="Можно вписать своё упражнение прямо в поле ↑",
                     font=self.f["small"], text_color=p["text_dim"]).pack(anchor="w", pady=(4, 10))

        # Вес / повторы / подходы / RPE
        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.pack(fill="x", pady=4)
        for i in range(4):
            row2.grid_columnconfigure(i, weight=1)

        u = app.config.units
        self.weight_entry = self._field(row2, 0, f"Вес, {u}")
        self.reps_entry = self._field(row2, 1, "Повторы")
        self.sets_entry = self._field(row2, 2, "Подходы")
        self.rpe_entry = self._field(row2, 3, "RPE 1–10 (опц.)")

        # Дата и заметка
        row3 = ctk.CTkFrame(inner, fg_color="transparent")
        row3.pack(fill="x", pady=(10, 4))
        row3.grid_columnconfigure(1, weight=1)

        self.date_entry = ctk.CTkEntry(row3, width=140, height=40, font=self.f["body"],
                                       fg_color=p["card_2"])
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=0, padx=(0, 6))

        self.notes_entry = ctk.CTkEntry(row3, placeholder_text="Заметка (самочувствие, техника...)",
                                        height=40, font=self.f["body"], fg_color=p["card_2"])
        self.notes_entry.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.msg = ctk.CTkLabel(inner, text="", font=self.f["body"])
        self.msg.pack(anchor="w", pady=(10, 0))

        ctk.CTkButton(inner, text="Сохранить подход ✓", height=48, font=self.f["h3"],
                      fg_color=self.a["main"], hover_color=self.a["hover"],
                      command=self._save).pack(fill="x", pady=(6, 0))

    def _field(self, master, col, placeholder):
        e = ctk.CTkEntry(master, placeholder_text=placeholder, height=40,
                         font=self.f["body"], fg_color=self.p["card_2"])
        e.grid(row=0, column=col, sticky="ew",
               padx=(0 if col == 0 else 4, 4 if col < 3 else 0))
        return e

    def _exercises_for(self, group):
        if group == "Все":
            merged = [e for lst in self.library.values() for e in lst]
            return merged + [e for e in self.app.db.get_exercises_used() if e not in merged]
        return self.library.get(group, [])

    def _on_group_change(self, group):
        values = self._exercises_for(group)
        self.exercise_combo.configure(values=values)
        if values:
            self.exercise_combo.set(values[0])

    def _save(self):
        ex = self.exercise_combo.get().strip()
        if not ex:
            return self._error("Выбери или впиши упражнение")
        try:
            weight = float(self.weight_entry.get().replace(",", ".") or 0)
            reps = int(self.reps_entry.get() or 0)
            sets = int(self.sets_entry.get() or 1)
        except ValueError:
            return self._error("Вес — число, повторы и подходы — целые числа")
        if reps <= 0 or sets <= 0:
            return self._error("Повторы и подходы должны быть больше нуля")

        rpe = None
        if self.rpe_entry.get().strip():
            try:
                rpe = max(1, min(10, int(self.rpe_entry.get())))
            except ValueError:
                return self._error("RPE — целое число от 1 до 10")

        date = self.date_entry.get().strip()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return self._error("Дата в формате ГГГГ-ММ-ДД")

        self.app.db.add_workout(date, ex, weight, reps, sets, rpe,
                                self.notes_entry.get())
        self.msg.configure(text=f"Записала: {ex} — {weight:g} × {reps} × {sets} 💪",
                           text_color=self.a["main"])
        self.notes_entry.delete(0, "end")

    def _error(self, text):
        self.msg.configure(text=text, text_color=self.p["danger"])

"""Настройки: тема, акцентный цвет, единицы, профиль, вес тела, экспорт, сброс."""
from datetime import datetime
from tkinter import filedialog
import customtkinter as ctk
from ..config import ACCENTS, GOALS
from .theme import fonts
from .widgets import Card, page_title


class SettingsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        self.app = app
        self.p = p
        self.f = fonts()
        self.a = app.config.accent
        cfg = app.config

        page_title(self, p, "⚙️ Настройки")

        # ---------- Внешний вид ----------
        card = self._section("Внешний вид")

        row = self._row(card, "Тема")
        seg = ctk.CTkSegmentedButton(row, values=["Тёмная", "Светлая"], height=34,
                                     selected_color=self.a["main"],
                                     selected_hover_color=self.a["hover"],
                                     command=self._set_theme)
        seg.set("Тёмная" if cfg.settings["theme"] == "dark" else "Светлая")
        seg.pack(side="right")

        row = self._row(card, "Акцентный цвет")
        colors = ctk.CTkFrame(row, fg_color="transparent")
        colors.pack(side="right")
        for name, col in ACCENTS.items():
            border = 2 if name == cfg.settings["accent"] else 0
            ctk.CTkButton(colors, text="", width=30, height=30, corner_radius=15,
                          fg_color=col["main"], hover_color=col["hover"],
                          border_width=border, border_color=p["text"],
                          command=lambda n=name: self._set_accent(n)).pack(side="left", padx=4)

        row = self._row(card, "Единицы веса")
        useg = ctk.CTkSegmentedButton(row, values=["кг", "lb"], height=34,
                                      selected_color=self.a["main"],
                                      selected_hover_color=self.a["hover"],
                                      command=self._set_units)
        useg.set(cfg.settings["units"])
        useg.pack(side="right")

        # ---------- Профиль ----------
        card = self._section("Профиль")

        row = self._row(card, "Имя")
        self.name_entry = ctk.CTkEntry(row, width=200, height=34, fg_color=p["card_2"])
        self.name_entry.insert(0, cfg.profile["name"])
        self.name_entry.pack(side="right")

        row = self._row(card, "Цель")
        gmenu = ctk.CTkOptionMenu(row, values=GOALS, height=34, width=200,
                                  fg_color=p["card_2"], button_color=self.a["main"],
                                  button_hover_color=self.a["hover"],
                                  command=self._set_goal)
        gmenu.set(cfg.profile["goal"])
        gmenu.pack(side="right")

        row = self._row(card, f'Записать вес тела ({cfg.units})')
        wrap = ctk.CTkFrame(row, fg_color="transparent")
        wrap.pack(side="right")
        self.bw_entry = ctk.CTkEntry(wrap, width=110, height=34, fg_color=p["card_2"])
        self.bw_entry.pack(side="left", padx=(0, 6))
        ctk.CTkButton(wrap, text="Сохранить", width=100, height=34,
                      fg_color=self.a["main"], hover_color=self.a["hover"],
                      command=self._save_profile).pack(side="left")

        # ---------- Данные ----------
        card = self._section("Данные")

        row = self._row(card, "Экспорт всех записей в CSV")
        ctk.CTkButton(row, text="Экспортировать", width=150, height=34,
                      fg_color=self.a["main"], hover_color=self.a["hover"],
                      command=self._export).pack(side="right")

        row = self._row(card, "Удалить все данные (безвозвратно)")
        ctk.CTkButton(row, text="Сбросить", width=150, height=34,
                      fg_color="transparent", border_width=1,
                      border_color=p["danger"], text_color=p["danger"],
                      hover_color=p["danger"],
                      command=self._reset).pack(side="right")

        self.msg = ctk.CTkLabel(self, text="", font=self.f["body"],
                                text_color=self.a["main"])
        self.msg.pack(anchor="w", padx=28, pady=(4, 20))

    # ---------- Помощники ----------

    def _section(self, title):
        ctk.CTkLabel(self, text=title, font=self.f["h2"],
                     text_color=self.p["text"]).pack(anchor="w", padx=28, pady=(20, 6))
        card = Card(self, self.p)
        card.pack(fill="x", padx=24)
        return card

    def _row(self, card, label):
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=8)
        ctk.CTkLabel(row, text=label, font=self.f["body"],
                     text_color=self.p["text"]).pack(side="left")
        return row

    # ---------- Действия ----------

    def _set_theme(self, value):
        self.app.config.settings["theme"] = "dark" if value == "Тёмная" else "light"
        self.app.config.save()
        self.app.rebuild(show="settings")

    def _set_accent(self, name):
        self.app.config.settings["accent"] = name
        self.app.config.save()
        self.app.rebuild(show="settings")

    def _set_units(self, value):
        self.app.config.settings["units"] = value
        self.app.config.save()
        self.app.rebuild(show="settings")

    def _set_goal(self, value):
        self.app.config.profile["goal"] = value
        self.app.config.save()

    def _save_profile(self):
        cfg = self.app.config
        cfg.profile["name"] = self.name_entry.get().strip() or cfg.profile["name"]
        bw = self.bw_entry.get().strip().replace(",", ".")
        if bw:
            try:
                weight = float(bw)
                cfg.profile["body_weight"] = weight
                self.app.db.add_body_weight(datetime.now().strftime("%Y-%m-%d"), weight)
            except ValueError:
                self.msg.configure(text="Вес должен быть числом", text_color=self.p["danger"])
                return
        cfg.save()
        self.msg.configure(text="Профиль сохранён ✓", text_color=self.a["main"])

    def _export(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile="gymlog_export.csv",
            filetypes=[("CSV", "*.csv")])
        if path:
            n = self.app.db.export_csv(path)
            self.msg.configure(text=f"Экспортировала {n} записей ✓",
                               text_color=self.a["main"])

    def _reset(self):
        if not getattr(self, "_confirm_reset", False):
            self._confirm_reset = True
            self.msg.configure(text="Точно? Нажми «Сбросить» ещё раз для подтверждения",
                               text_color=self.p["danger"])
            return
        self.app.db.reset_all()
        self._confirm_reset = False
        self.msg.configure(text="Все данные удалены", text_color=self.p["danger"])

"""Онбординг: настройка профиля при первом запуске."""
import customtkinter as ctk
from ..config import GOALS, ACCENTS
from .theme import fonts


class OnboardingFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        self.app = app
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        f = fonts()
        a = app.config.accent

        box = ctk.CTkFrame(self, fg_color=p["card"], corner_radius=18)
        box.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(box, fg_color="transparent")
        inner.pack(padx=48, pady=40)

        ctk.CTkLabel(inner, text="💪 GymLog", font=(f["h1"][0], 34, "bold"),
                     text_color=a["main"]).pack(pady=(0, 4))
        ctk.CTkLabel(inner, text="Твой личный трекер тренировок.\nПара вопросов — и погнали.",
                     font=f["body"], text_color=p["text_dim"], justify="center").pack(pady=(0, 24))

        self.name_entry = ctk.CTkEntry(inner, placeholder_text="Как тебя зовут?",
                                       width=300, height=42, font=f["body"])
        self.name_entry.pack(pady=6)

        self.weight_entry = ctk.CTkEntry(inner, placeholder_text="Твой вес, кг (необязательно)",
                                         width=300, height=42, font=f["body"])
        self.weight_entry.pack(pady=6)

        ctk.CTkLabel(inner, text="Главная цель", font=f["small"],
                     text_color=p["text_dim"]).pack(anchor="w", pady=(14, 4))
        self.goal_seg = ctk.CTkSegmentedButton(inner, values=GOALS, height=36,
                                               selected_color=a["main"],
                                               selected_hover_color=a["hover"])
        self.goal_seg.set(GOALS[0])
        self.goal_seg.pack(fill="x")

        ctk.CTkLabel(inner, text="Акцентный цвет", font=f["small"],
                     text_color=p["text_dim"]).pack(anchor="w", pady=(14, 4))
        colors_row = ctk.CTkFrame(inner, fg_color="transparent")
        colors_row.pack()
        self._accent_var = ctk.StringVar(value=app.config.settings["accent"])
        for name, col in ACCENTS.items():
            btn = ctk.CTkButton(colors_row, text="", width=36, height=36, corner_radius=18,
                                fg_color=col["main"], hover_color=col["hover"],
                                command=lambda n=name: self._pick_accent(n))
            btn.pack(side="left", padx=5)

        self.error_lbl = ctk.CTkLabel(inner, text="", font=f["small"],
                                      text_color=p["danger"])
        self.error_lbl.pack(pady=(10, 0))

        ctk.CTkButton(inner, text="Начать тренироваться →", height=46, font=f["h3"],
                      fg_color=a["main"], hover_color=a["hover"],
                      command=self._finish).pack(fill="x", pady=(8, 0))

    def _pick_accent(self, name):
        self._accent_var.set(name)
        self.app.config.settings["accent"] = name
        self.app.config.save()
        self.app.rebuild(show="onboarding")

    def _finish(self):
        name = self.name_entry.get().strip()
        if not name:
            self.error_lbl.configure(text="Напиши имя — так будет уютнее :)")
            return
        weight = 0.0
        w_raw = self.weight_entry.get().strip().replace(",", ".")
        if w_raw:
            try:
                weight = float(w_raw)
            except ValueError:
                self.error_lbl.configure(text="Вес должен быть числом")
                return
        cfg = self.app.config
        cfg.profile.update({
            "name": name,
            "body_weight": weight,
            "goal": self.goal_seg.get(),
            "onboarded": True,
        })
        cfg.settings["accent"] = self._accent_var.get()
        cfg.save()
        if weight:
            from datetime import datetime
            self.app.db.add_body_weight(datetime.now().strftime("%Y-%m-%d"), weight)
        self.app.rebuild(show="dashboard")

"""
GymLog — трекер тренировок.
Python 3.10+ · CustomTkinter · SQLite · Matplotlib
Запуск: python main.py
"""
import customtkinter as ctk
from app.config import Config
from app.database import Database
from app.ui.theme import PALETTES, fonts
from app.ui.onboarding import OnboardingFrame
from app.ui.dashboard import DashboardFrame
from app.ui.workout_page import WorkoutFrame
from app.ui.history_page import HistoryFrame
from app.ui.charts_page import ChartsFrame
from app.ui.records_page import RecordsFrame
from app.ui.settings_page import SettingsFrame

PAGES = {
    "dashboard": ("🏠  Главная", DashboardFrame),
    "workout":   ("➕  Тренировка", WorkoutFrame),
    "history":   ("📜  История", HistoryFrame),
    "charts":    ("📈  Прогресс", ChartsFrame),
    "records":   ("🏆  Рекорды", RecordsFrame),
    "settings":  ("⚙️  Настройки", SettingsFrame),
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config_ = Config()
        self.db = Database()

        self.title("GymLog — трекер тренировок")
        self.geometry("1100x720")
        self.minsize(920, 620)

        self._current_page = "dashboard"
        self.rebuild(show=None)

    # config — уже метод tkinter, поэтому храним под другим именем
    @property
    def config(self):  # noqa: A003
        return self.config_

    @property
    def palette(self):
        return PALETTES[self.config_.settings["theme"]]

    def rebuild(self, show=None):
        """Полная пересборка UI (после смены темы/акцента/онбординга)."""
        ctk.set_appearance_mode(self.config_.settings["theme"])
        for w in self.winfo_children():
            w.destroy()

        if not self.config_.profile["onboarded"] or show == "onboarding":
            OnboardingFrame(self, self).pack(fill="both", expand=True)
            return

        p = self.palette
        self.configure(fg_color=p["bg"])
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color=p["bg"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")

        self.show_page(show or self._current_page)

    def _build_sidebar(self):
        p = self.palette
        a = self.config_.accent
        f = fonts()

        sidebar = ctk.CTkFrame(self, fg_color=p["sidebar"], corner_radius=0, width=230)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="💪 GymLog", font=(f["h1"][0], 24, "bold"),
                     text_color=a["main"]).pack(padx=24, pady=(28, 2), anchor="w")
        name = self.config_.profile["name"]
        if name:
            ctk.CTkLabel(sidebar, text=name, font=f["small"],
                         text_color=p["text_dim"]).pack(padx=26, anchor="w")

        spacer = ctk.CTkFrame(sidebar, fg_color="transparent", height=18)
        spacer.pack()

        self._nav_buttons = {}
        for key, (label, _) in PAGES.items():
            active = key == self._current_page
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w", height=44, corner_radius=10,
                font=f["body"],
                fg_color=a["soft"] if active else "transparent",
                text_color=p["text"] if active else p["text_dim"],
                hover_color=p["card"],
                command=lambda k=key: self.show_page(k),
            )
            btn.pack(fill="x", padx=14, pady=2)
            self._nav_buttons[key] = btn

        ctk.CTkLabel(sidebar, text="v1.0 · made with 🐍", font=f["small"],
                     text_color=p["text_dim"]).pack(side="bottom", pady=16)

    def show_page(self, key):
        self._current_page = key
        p = self.palette
        a = self.config_.accent

        for k, btn in self._nav_buttons.items():
            btn.configure(
                fg_color=a["soft"] if k == key else "transparent",
                text_color=p["text"] if k == key else p["text_dim"],
            )

        for w in self.content.winfo_children():
            w.destroy()
        PAGES[key][1](self.content, self).pack(fill="both", expand=True)

    def destroy(self):
        self.db.close()
        super().destroy()


if __name__ == "__main__":
    App().mainloop()

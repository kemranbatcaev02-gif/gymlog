"""Графики прогресса: вес, объём, расчётный 1ПМ, вес тела."""
import customtkinter as ctk
import matplotlib
matplotlib.use("Agg")  # без системного бэкенда; ниже переключаемся на TkAgg-канвас
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime
from .theme import fonts
from .widgets import page_title

METRICS = {
    "Рабочий вес": 1,
    "Объём (тоннаж)": 2,
    "Расчётный 1ПМ": 3,
}


class ChartsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        p = app.palette
        super().__init__(master, fg_color=p["bg"])
        self.app = app
        self.p = p
        self.f = fonts()
        self.a = app.config.accent
        self.canvas = None

        page_title(self, p, "📈 Прогресс", "Выбери упражнение и метрику")

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=24, pady=(14, 6))

        exercises = app.db.get_exercises_used()
        bw = app.db.get_body_weight()
        options = exercises + (["— Вес тела —"] if bw else [])

        if not options:
            ctk.CTkLabel(self, text="Добавь пару тренировок — и здесь появятся графики 📊",
                         font=self.f["body"], text_color=p["text_dim"]).pack(pady=40)
            return

        self.ex_menu = ctk.CTkOptionMenu(bar, values=options, height=36,
                                         fg_color=p["card"], button_color=self.a["main"],
                                         button_hover_color=self.a["hover"],
                                         font=self.f["body"], command=lambda _: self._render())
        self.ex_menu.pack(side="left", padx=(0, 8))

        self.metric_seg = ctk.CTkSegmentedButton(bar, values=list(METRICS), height=36,
                                                 selected_color=self.a["main"],
                                                 selected_hover_color=self.a["hover"],
                                                 command=lambda _: self._render())
        self.metric_seg.set("Рабочий вес")
        self.metric_seg.pack(side="left")

        self.chart_holder = ctk.CTkFrame(self, fg_color=p["card"], corner_radius=14)
        self.chart_holder.pack(fill="both", expand=True, padx=24, pady=(8, 20))
        self._render()

    def _render(self):
        for w in self.chart_holder.winfo_children():
            w.destroy()

        choice = self.ex_menu.get()
        if choice == "— Вес тела —":
            rows = self.app.db.get_body_weight()
            dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in rows]
            values = [r["weight"] for r in rows]
            title = "Вес тела"
            ylabel = self.app.config.units
        else:
            d, weights, volumes, one_rm = self.app.db.get_progress(choice)
            dates = [datetime.strptime(x, "%Y-%m-%d") for x in d]
            idx = METRICS[self.metric_seg.get()]
            values = [weights, volumes, one_rm][idx - 1]
            title = f"{choice} — {self.metric_seg.get().lower()}"
            ylabel = self.app.config.units

        if len(dates) < 1:
            ctk.CTkLabel(self.chart_holder, text="Мало данных для графика",
                         font=self.f["body"], text_color=self.p["text_dim"]).pack(pady=40)
            return

        p, a = self.p, self.a
        fig = Figure(figsize=(8, 4.4), dpi=100, facecolor=p["chart_bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(p["chart_bg"])

        ax.plot(dates, values, color=a["main"], linewidth=2.4,
                marker="o", markersize=6, markerfacecolor=a["main"],
                markeredgecolor=p["chart_bg"], markeredgewidth=1.5)
        ax.fill_between(dates, values, min(values) * 0.97 if min(values) > 0 else 0,
                        color=a["main"], alpha=0.12)

        ax.set_title(title, color=p["text"], fontsize=13, fontweight="bold", pad=14)
        ax.set_ylabel(ylabel, color=p["text_dim"], fontsize=10)
        ax.tick_params(colors=p["text_dim"], labelsize=9)
        ax.grid(True, color=p["chart_grid"], linewidth=0.7, alpha=0.6)
        for spine in ax.spines.values():
            spine.set_color(p["chart_grid"])
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
        fig.autofmt_xdate(rotation=30)
        fig.tight_layout(pad=2)

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_holder)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

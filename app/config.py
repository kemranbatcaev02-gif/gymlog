"""Настройки приложения и профиль пользователя (JSON)."""
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "config.json"

DEFAULTS = {
    "profile": {
        "name": "",
        "body_weight": 0.0,
        "goal": "Сила",          # Сила / Масса / Похудение / Выносливость
        "onboarded": False,
    },
    "settings": {
        "theme": "dark",          # dark / light
        "accent": "emerald",      # emerald / blue / violet / amber / rose
        "units": "кг",            # кг / lb
    },
}

ACCENTS = {
    "emerald": {"main": "#10b981", "hover": "#059669", "soft": "#064e3b"},
    "blue":    {"main": "#3b82f6", "hover": "#2563eb", "soft": "#1e3a5f"},
    "violet":  {"main": "#8b5cf6", "hover": "#7c3aed", "soft": "#3b2a63"},
    "amber":   {"main": "#f59e0b", "hover": "#d97706", "soft": "#573f10"},
    "rose":    {"main": "#f43f5e", "hover": "#e11d48", "soft": "#551a26"},
}

GOALS = ["Сила", "Масса", "Похудение", "Выносливость"]


class Config:
    def __init__(self, path: Path = CONFIG_PATH):
        self.path = path
        self.data = json.loads(json.dumps(DEFAULTS))  # глубокая копия
        self.load()

    def load(self):
        if self.path.exists():
            try:
                stored = json.loads(self.path.read_text(encoding="utf-8"))
                for section in self.data:
                    self.data[section].update(stored.get(section, {}))
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # Удобные шорткаты
    @property
    def profile(self):
        return self.data["profile"]

    @property
    def settings(self):
        return self.data["settings"]

    @property
    def accent(self):
        return ACCENTS.get(self.settings["accent"], ACCENTS["emerald"])

    @property
    def units(self):
        return self.settings["units"]

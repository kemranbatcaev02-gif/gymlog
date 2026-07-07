"""Палитра и типографика приложения."""

PALETTES = {
    "dark": {
        "bg":        "#0f1115",
        "sidebar":   "#161a21",
        "card":      "#1c212b",
        "card_2":    "#242a36",
        "border":    "#2c3340",
        "text":      "#eef1f6",
        "text_dim":  "#8b93a3",
        "danger":    "#ef4444",
        "chart_bg":  "#1c212b",
        "chart_grid":"#2c3340",
    },
    "light": {
        "bg":        "#f2f4f8",
        "sidebar":   "#e6e9f0",
        "card":      "#ffffff",
        "card_2":    "#eef1f6",
        "border":    "#d7dbe4",
        "text":      "#1a1f29",
        "text_dim":  "#68707f",
        "danger":    "#dc2626",
        "chart_bg":  "#ffffff",
        "chart_grid":"#e2e6ee",
    },
}

FONT = "Segoe UI"

def fonts():
    """Готовые кортежи шрифтов (tkinter-совместимые)."""
    return {
        "h1":    (FONT, 26, "bold"),
        "h2":    (FONT, 18, "bold"),
        "h3":    (FONT, 14, "bold"),
        "body":  (FONT, 13),
        "small": (FONT, 11),
        "stat":  (FONT, 30, "bold"),
    }

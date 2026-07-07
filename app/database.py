"""Слой работы с базой данных SQLite."""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "gymlog.db"


class Database:
    def __init__(self, path: Path = DB_PATH):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS workouts (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                date      TEXT NOT NULL,
                exercise  TEXT NOT NULL,
                weight    REAL NOT NULL DEFAULT 0,
                reps      INTEGER NOT NULL DEFAULT 0,
                sets      INTEGER NOT NULL DEFAULT 1,
                rpe       INTEGER,
                notes     TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS body_weight (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                date   TEXT NOT NULL,
                weight REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_workouts_exercise ON workouts(exercise);
            CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date);
            """
        )
        self.conn.commit()

    # ---------- Тренировки ----------

    def add_workout(self, date, exercise, weight, reps, sets, rpe=None, notes=""):
        self.conn.execute(
            "INSERT INTO workouts (date, exercise, weight, reps, sets, rpe, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (date, exercise.strip(), weight, reps, sets, rpe, notes.strip()),
        )
        self.conn.commit()

    def delete_workout(self, workout_id: int):
        self.conn.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
        self.conn.commit()

    def get_workouts(self, exercise=None, date_from=None, date_to=None, limit=None):
        query = "SELECT * FROM workouts WHERE 1=1"
        params = []
        if exercise:
            query += " AND exercise = ?"
            params.append(exercise)
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
        query += " ORDER BY date DESC, id DESC"
        if limit:
            query += f" LIMIT {int(limit)}"
        return self.conn.execute(query, params).fetchall()

    def get_exercises_used(self):
        rows = self.conn.execute(
            "SELECT DISTINCT exercise FROM workouts ORDER BY exercise"
        ).fetchall()
        return [r["exercise"] for r in rows]

    # ---------- Статистика ----------

    @staticmethod
    def epley_1rm(weight: float, reps: int) -> float:
        """Оценка одноповторного максимума по формуле Эпли."""
        if reps <= 1:
            return weight
        return round(weight * (1 + reps / 30), 1)

    def get_personal_records(self):
        """Лучший вес, лучший расчётный 1ПМ и дата для каждого упражнения."""
        records = {}
        for row in self.conn.execute("SELECT * FROM workouts"):
            est = self.epley_1rm(row["weight"], row["reps"])
            rec = records.get(row["exercise"])
            if rec is None or est > rec["est_1rm"]:
                records[row["exercise"]] = {
                    "weight": row["weight"],
                    "reps": row["reps"],
                    "est_1rm": est,
                    "date": row["date"],
                }
        return dict(sorted(records.items()))

    def get_stats(self):
        """Сводка для дашборда."""
        c = self.conn
        total = c.execute("SELECT COUNT(*) n FROM workouts").fetchone()["n"]
        volume = c.execute(
            "SELECT COALESCE(SUM(weight * reps * sets), 0) v FROM workouts"
        ).fetchone()["v"]

        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        week = c.execute(
            "SELECT COUNT(DISTINCT date) n FROM workouts WHERE date >= ?", (week_ago,)
        ).fetchone()["n"]

        days = [r["date"] for r in c.execute(
            "SELECT DISTINCT date FROM workouts ORDER BY date DESC"
        )]
        streak = self._calc_streak(days)
        return {
            "total_entries": total,
            "total_volume": volume,
            "workouts_this_week": week,
            "streak": streak,
            "exercises_count": len(self.get_exercises_used()),
        }

    @staticmethod
    def _calc_streak(days: list[str]) -> int:
        """Серия тренировочных дней: считается, если между днями не больше 1 дня отдыха."""
        if not days:
            return 0
        dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in days]
        today = datetime.now().date()
        if (today - dates[0]).days > 2:
            return 0
        streak = 1
        for prev, cur in zip(dates, dates[1:]):
            if (prev - cur).days <= 2:
                streak += 1
            else:
                break
        return streak

    def get_progress(self, exercise: str):
        """(даты, лучший вес за день, объём за день, 1ПМ за день) для графиков."""
        rows = self.conn.execute(
            "SELECT date, weight, reps, sets FROM workouts WHERE exercise = ? ORDER BY date",
            (exercise,),
        ).fetchall()
        by_day: dict[str, dict] = {}
        for r in rows:
            d = by_day.setdefault(r["date"], {"weight": 0, "volume": 0, "est_1rm": 0})
            d["weight"] = max(d["weight"], r["weight"])
            d["volume"] += r["weight"] * r["reps"] * r["sets"]
            d["est_1rm"] = max(d["est_1rm"], self.epley_1rm(r["weight"], r["reps"]))
        dates = list(by_day.keys())
        return (
            dates,
            [by_day[d]["weight"] for d in dates],
            [by_day[d]["volume"] for d in dates],
            [by_day[d]["est_1rm"] for d in dates],
        )

    # ---------- Вес тела ----------

    def add_body_weight(self, date: str, weight: float):
        self.conn.execute(
            "INSERT INTO body_weight (date, weight) VALUES (?, ?)", (date, weight)
        )
        self.conn.commit()

    def get_body_weight(self):
        return self.conn.execute(
            "SELECT * FROM body_weight ORDER BY date"
        ).fetchall()

    # ---------- Сервис ----------

    def export_csv(self, path: str):
        import csv
        rows = self.get_workouts()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Дата", "Упражнение", "Вес", "Повторы", "Подходы", "RPE", "Заметки"])
            for r in rows:
                w.writerow([r["date"], r["exercise"], r["weight"],
                            r["reps"], r["sets"], r["rpe"] or "", r["notes"]])
        return len(rows)

    def reset_all(self):
        self.conn.executescript("DELETE FROM workouts; DELETE FROM body_weight;")
        self.conn.commit()

    def close(self):
        self.conn.close()

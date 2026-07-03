import sqlite3
from pathlib import Path
from datetime import datetime
import csv
import json

DB_PATH = Path("greenwich_bot.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            language TEXT,
            country TEXT,
            visa_type TEXT,
            score INTEGER,
            strengths TEXT,
            risks TEXT,
            recommendations TEXT,
            answers_json TEXT,
            created_at TEXT
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            username TEXT,
            language TEXT,
            country TEXT,
            visa_type TEXT,
            score INTEGER,
            name TEXT,
            phone TEXT,
            email TEXT,
            preferred_time TEXT,
            comment TEXT,
            answers_json TEXT,
            created_at TEXT
        )
        """)

        conn.commit()


def upsert_user(telegram_id: int, username: str, first_name: str, language: str | None = None) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        existing = conn.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE users SET username=?, first_name=?, language=COALESCE(?, language), updated_at=? WHERE telegram_id=?",
                (username, first_name, language, now, telegram_id),
            )
        else:
            conn.execute(
                "INSERT INTO users (telegram_id, username, first_name, language, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (telegram_id, username, first_name, language, now, now),
            )
        conn.commit()


def save_assessment(data: dict) -> int:
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO assessments
            (telegram_id, language, country, visa_type, score, strengths, risks, recommendations, answers_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("telegram_id"),
                data.get("lang"),
                data.get("country"),
                data.get("visa_type"),
                data.get("score"),
                json.dumps(data.get("strengths", []), ensure_ascii=False),
                json.dumps(data.get("risks", []), ensure_ascii=False),
                json.dumps(data.get("recommendations", []), ensure_ascii=False),
                json.dumps(data.get("answers", {}), ensure_ascii=False),
                now,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def save_lead(data: dict) -> int:
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO leads
            (telegram_id, username, language, country, visa_type, score, name, phone, email, preferred_time, comment, answers_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("telegram_id"),
                data.get("username"),
                data.get("lang"),
                data.get("country"),
                data.get("visa_type"),
                data.get("score"),
                data.get("name"),
                data.get("phone"),
                data.get("email"),
                data.get("preferred_time"),
                data.get("comment"),
                json.dumps(data.get("answers", {}), ensure_ascii=False),
                now,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def get_stats() -> dict:
    with get_connection() as conn:
        users = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        assessments = conn.execute("SELECT COUNT(*) AS c FROM assessments").fetchone()["c"]
        leads = conn.execute("SELECT COUNT(*) AS c FROM leads").fetchone()["c"]
        avg_score_row = conn.execute("SELECT AVG(score) AS avg_score FROM assessments").fetchone()
        avg_score = avg_score_row["avg_score"] if avg_score_row and avg_score_row["avg_score"] is not None else 0
        top_countries = conn.execute("""
            SELECT country, COUNT(*) AS c
            FROM assessments
            GROUP BY country
            ORDER BY c DESC
            LIMIT 5
        """).fetchall()

    conversion = round((leads / assessments * 100), 1) if assessments else 0
    return {
        "users": users,
        "assessments": assessments,
        "leads": leads,
        "avg_score": round(avg_score, 1),
        "conversion": conversion,
        "top_countries": [(r["country"], r["c"]) for r in top_countries],
    }


def export_leads_csv(path: Path = Path("greenwich_leads_export.csv")) -> Path:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()

    fieldnames = [
        "id", "created_at", "telegram_id", "username", "language", "country", "visa_type",
        "score", "name", "phone", "email", "preferred_time", "comment", "answers_json"
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fieldnames})

    return path

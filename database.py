import sqlite3
from datetime import datetime
from typing import Optional
from config import DB_PATH, REFERRAL_BONUS


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            full_name TEXT,
            phone TEXT,
            age INTEGER,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            referral_bonus INTEGER DEFAULT 0,
            registered_at TEXT,
            username TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price TEXT,
            duration TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course_id INTEGER,
            enrolled_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(telegram_id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()


# ── Settings (gif_id saqlash) ──────────────────────────
def get_setting(key: str) -> Optional[str]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def set_setting(key: str, value: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()


# ── Users ──────────────────────────────────────────────
def get_user(telegram_id: int) -> Optional[dict]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    if row:
        keys = ["id","telegram_id","full_name","phone","age","referral_code",
                "referred_by","referral_bonus","registered_at","username"]
        return dict(zip(keys, row))
    return None


def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY registered_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def create_user(telegram_id, full_name, phone, age, username, referred_by=None):
    ref_code = f"GS{telegram_id}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO users
        (telegram_id, full_name, phone, age, referral_code, referred_by, registered_at, username)
        VALUES (?,?,?,?,?,?,?,?)
    """, (telegram_id, full_name, phone, age, ref_code, referred_by, now, username or ""))
    if referred_by:
        c.execute("UPDATE users SET referral_bonus=referral_bonus+? WHERE telegram_id=?",
                  (REFERRAL_BONUS, referred_by))
    conn.commit()
    conn.close()


def update_user(telegram_id, full_name, phone, age):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET full_name=?, phone=?, age=? WHERE telegram_id=?",
              (full_name, phone, age, telegram_id))
    conn.commit()
    conn.close()


def get_referral_count(telegram_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (telegram_id,))
    count = c.fetchone()[0]
    conn.close()
    return count


# ── Courses ────────────────────────────────────────────
def get_all_courses():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM courses ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def get_course(course_id) -> Optional[dict]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(zip(["id","name","description","price","duration","created_at"], row))
    return None


def add_course(name, description, price, duration):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO courses (name,description,price,duration,created_at) VALUES (?,?,?,?,?)",
              (name, description, price, duration, now))
    conn.commit()
    conn.close()


def update_course(course_id, name, description, price, duration):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE courses SET name=?,description=?,price=?,duration=? WHERE id=?",
              (name, description, price, duration, course_id))
    conn.commit()
    conn.close()


def delete_course(course_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM courses WHERE id=?", (course_id,))
    conn.commit()
    conn.close()


# ── Enrollments ────────────────────────────────────────
def enroll_user(user_id, course_id) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM enrollments WHERE user_id=? AND course_id=?", (user_id, course_id))
    if c.fetchone():
        conn.close()
        return False
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO enrollments (user_id,course_id,enrolled_at) VALUES (?,?,?)",
              (user_id, course_id, now))
    conn.commit()
    conn.close()
    return True


def get_enrollments_for_course(course_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT u.full_name, u.phone, u.username, e.enrolled_at
        FROM enrollments e JOIN users u ON e.user_id=u.telegram_id
        WHERE e.course_id=?
        ORDER BY e.enrolled_at DESC
    """, (course_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_enrollments_for_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT c.name, c.price, e.enrolled_at
        FROM enrollments e JOIN courses c ON e.course_id=c.id
        WHERE e.user_id=?
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


# ── Stats ──────────────────────────────────────────────
def get_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users");       total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM courses");     total_courses = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM enrollments"); total_enrollments = c.fetchone()[0]
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM users WHERE registered_at LIKE ?", (f"{today}%",))
    today_users = c.fetchone()[0]
    conn.close()
    return total_users, total_courses, total_enrollments, today_users


def get_current_time() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M')

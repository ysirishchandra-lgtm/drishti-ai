"""SQLite persistence layer for DRISHTI-AI screening records.

Privacy & Architecture Notice:
- Only metadata, technical quality metrics, and screening workflow statuses are stored.
- Raw retinal image bytes are NOT stored inside the database.
- Personal identifying information is intentionally excluded in adherence to privacy-by-design.
"""
from datetime import datetime, timezone
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "drishti.db")


def get_db_path() -> str:
    """Return database file path, honoring environment variable if provided."""
    return os.getenv("DRISHTI_DB_PATH", DEFAULT_DB_PATH)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create a connection with row-factory enabled."""
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize SQLite tables and indexes."""
    path = db_path or get_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with get_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS screenings (
                screening_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                validation_passed INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                format TEXT NOT NULL,
                aspect_ratio REAL NOT NULL,
                mean_brightness REAL NOT NULL,
                contrast_std REAL NOT NULL,
                heuristic_status TEXT NOT NULL,
                rejection_reasons TEXT,
                model_status TEXT NOT NULL DEFAULT 'not_configured',
                analysis_available INTEGER NOT NULL DEFAULT 0,
                prediction TEXT,
                confidence REAL,
                class_probabilities TEXT,
                gradcam_available INTEGER NOT NULL DEFAULT 0,
                human_review_status TEXT NOT NULL DEFAULT 'pending',
                follow_up_status TEXT NOT NULL DEFAULT 'none',
                notes TEXT
            );
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_screenings_created_at 
            ON screenings(created_at DESC);
        """)
        conn.commit()


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert an SQLite row to a structured screening dictionary matching schemas."""
    data = dict(row)
    rejection_reasons = []
    if data.get("rejection_reasons"):
        try:
            rejection_reasons = json.loads(data["rejection_reasons"])
        except Exception:
            rejection_reasons = []

    class_probabilities = None
    if data.get("class_probabilities"):
        try:
            class_probabilities = json.loads(data["class_probabilities"])
        except Exception:
            class_probabilities = None

    return {
        "screening_id": data["screening_id"],
        "created_at": data["created_at"],
        "file_name": data["file_name"],
        "file_size_bytes": data["file_size_bytes"],
        "mime_type": data["mime_type"],
        "validation_passed": bool(data["validation_passed"]),
        "image_quality": {
            "width": data["width"],
            "height": data["height"],
            "format": data["format"],
            "channels": 3,
            "aspect_ratio": data["aspect_ratio"],
            "mean_brightness": data["mean_brightness"],
            "contrast_std": data["contrast_std"],
            "heuristic_status": data["heuristic_status"],
            "rejection_reasons": rejection_reasons,
            "disclaimer": "Preliminary technical usability heuristics only. Not a clinically validated image quality evaluation."
        },
        "model_status": data["model_status"],
        "analysis_available": bool(data["analysis_available"]),
        "prediction": data["prediction"],
        "confidence": data["confidence"],
        "class_probabilities": class_probabilities,
        "gradcam_available": bool(data["gradcam_available"]),
        "human_review_status": data["human_review_status"],
        "follow_up_status": data["follow_up_status"],
        "notes": data["notes"],
    }


def save_screening(record: Dict[str, Any], db_path: Optional[str] = None) -> None:
    """Insert a new screening record."""
    path = db_path or get_db_path()
    reasons_json = json.dumps(record["image_quality"].get("rejection_reasons", []))
    probs_json = json.dumps(record.get("class_probabilities")) if record.get("class_probabilities") else None

    with get_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO screenings (
                screening_id, created_at, file_name, file_size_bytes, mime_type,
                validation_passed, width, height, format, aspect_ratio,
                mean_brightness, contrast_std, heuristic_status, rejection_reasons,
                model_status, analysis_available, prediction, confidence,
                class_probabilities, gradcam_available, human_review_status,
                follow_up_status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record["screening_id"],
            record["created_at"],
            record["file_name"],
            record["file_size_bytes"],
            record["mime_type"],
            1 if record.get("validation_passed", True) else 0,
            record["image_quality"]["width"],
            record["image_quality"]["height"],
            record["image_quality"]["format"],
            record["image_quality"]["aspect_ratio"],
            record["image_quality"]["mean_brightness"],
            record["image_quality"]["contrast_std"],
            record["image_quality"]["heuristic_status"],
            reasons_json,
            record.get("model_status", "not_configured"),
            1 if record.get("analysis_available", False) else 0,
            record.get("prediction"),
            record.get("confidence"),
            probs_json,
            1 if record.get("gradcam_available", False) else 0,
            record.get("human_review_status", "pending"),
            record.get("follow_up_status", "none"),
            record.get("notes")
        ))
        conn.commit()


def get_screening(screening_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch a single screening record by ID."""
    path = db_path or get_db_path()
    with get_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM screenings WHERE screening_id = ?", (screening_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return row_to_dict(row)


def list_screenings(
    page: int = 1,
    page_size: int = 20,
    db_path: Optional[str] = None
) -> Tuple[int, List[Dict[str, Any]]]:
    """Return paginated screening records ordered from newest to oldest."""
    path = db_path or get_db_path()
    offset = max(0, (page - 1) * page_size)
    with get_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM screenings")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT * FROM screenings
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (page_size, offset))
        rows = cursor.fetchall()
        items = [row_to_dict(r) for r in rows]
        return total, items


def update_screening_analysis(
    screening_id: str,
    analysis_data: Dict[str, Any],
    db_path: Optional[str] = None
) -> bool:
    """Update analysis results for an existing screening record without duplication."""
    path = db_path or get_db_path()
    probs = analysis_data.get("class_probabilities")
    probs_json = json.dumps(probs) if probs is not None else None

    with get_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE screenings
            SET model_status = ?,
                analysis_available = ?,
                prediction = ?,
                confidence = ?,
                class_probabilities = ?,
                gradcam_available = ?,
                notes = ?
            WHERE screening_id = ?
        """, (
            analysis_data.get("model_status", "not_configured"),
            1 if analysis_data.get("analysis_available", False) else 0,
            analysis_data.get("prediction"),
            analysis_data.get("confidence"),
            probs_json,
            1 if analysis_data.get("gradcam_available", False) else 0,
            analysis_data.get("notes"),
            screening_id
        ))
        conn.commit()
        return cursor.rowcount > 0


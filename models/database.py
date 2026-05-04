"""
The Filing Cabinet (Database Manager).
This file handles saving our leads securely to a local SQLite database.
It also features a "Checkpointing" system. If the scraper crashes or the internet 
disconnects, this system remembers exactly where it stopped so it doesn't 
start from the beginning next time.
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Optional
from .schema import BusinessSchema
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Handles all reading and writing to the local 'leads.sqlite' file.
    """
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(str(self.db_path))

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            city TEXT NOT NULL,
            source_platform TEXT NOT NULL,
            data JSON NOT NULL,
            status TEXT DEFAULT 'raw',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scrape_checkpoints (
            city TEXT,
            platform TEXT,
            keyword TEXT,
            last_page INTEGER DEFAULT 0,
            status TEXT DEFAULT 'in_progress',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (city, platform, keyword)
        )
        ''')

        # Index for fast city lookups
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_leads_city ON leads(city)
        ''')

        conn.commit()
        conn.close()

    def save_lead(self, lead: BusinessSchema, source: str):
        conn = self._get_conn()
        cursor = conn.cursor()
        db_data = lead.model_dump_json()
        cursor.execute('''
        INSERT INTO leads (business_name, city, source_platform, data, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (lead.business_name, lead.city, source, db_data, lead.confidence_score))
        conn.commit()
        conn.close()

    def save_leads_batch(self, leads: List[BusinessSchema], source: str):
        if not leads:
            return
        conn = self._get_conn()
        cursor = conn.cursor()
        data_to_insert = [
            (l.business_name, l.city, source, l.model_dump_json(), l.confidence_score)
            for l in leads
        ]
        cursor.executemany('''
        INSERT INTO leads (business_name, city, source_platform, data, status)
        VALUES (?, ?, ?, ?, ?)
        ''', data_to_insert)
        conn.commit()
        conn.close()
        logger.info(f"Saved batch of {len(leads)} leads from {source}")

    def get_checkpoint(self, city: str, platform: str, keyword: str) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT last_page FROM scrape_checkpoints
        WHERE city = ? AND platform = ? AND keyword = ?
        ''', (city, platform, keyword))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0

    def update_checkpoint(self, city: str, platform: str, keyword: str, last_page: int, status: str = 'in_progress'):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO scrape_checkpoints (city, platform, keyword, last_page, status)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(city, platform, keyword)
        DO UPDATE SET last_page=excluded.last_page, status=excluded.status, updated_at=CURRENT_TIMESTAMP
        ''', (city, platform, keyword, last_page, status))
        conn.commit()
        conn.close()

    def load_all_leads(self) -> List[BusinessSchema]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM leads')
        rows = cursor.fetchall()
        leads = []
        for row in rows:
            try:
                leads.append(BusinessSchema.model_validate_json(row[0]))
            except Exception as e:
                logger.warning(f"Skipping corrupt record: {e}")
        conn.close()
        return leads

    def load_leads_by_city(self, city: str) -> List[BusinessSchema]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM leads WHERE LOWER(city) = LOWER(?)', (city,))
        rows = cursor.fetchall()
        leads = []
        for row in rows:
            try:
                leads.append(BusinessSchema.model_validate_json(row[0]))
            except Exception as e:
                logger.warning(f"Skipping corrupt record: {e}")
        conn.close()
        return leads

    def get_total_count(self) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM leads')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_city_counts(self) -> dict:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT city, COUNT(*) FROM leads GROUP BY city')
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}

    def is_checkpoint_completed(self, city: str, platform: str, keyword: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT status FROM scrape_checkpoints
        WHERE city = ? AND platform = ? AND keyword = ?
        ''', (city, platform, keyword))
        row = cursor.fetchone()
        conn.close()
        return row[0] == 'completed' if row else False

import os
from contextlib import contextmanager
from typing import Optional

import psycopg2


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn

    @contextmanager
    def conn(self):
        conn = psycopg2.connect(self.dsn, sslmode="require")
        try:
            yield conn
        finally:
            conn.close()

    def init_schema(self) -> None:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        selected_template TEXT,
                        stage TEXT DEFAULT 'await_template',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS uploads (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                        slot_index INTEGER NOT NULL CHECK (slot_index >= 1 AND slot_index <= 5),
                        telegram_file_id TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'uploaded',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, slot_index)
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS transactions (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                        invoice_payload TEXT NOT NULL UNIQUE,
                        telegram_payment_charge_id TEXT,
                        provider_payment_charge_id TEXT,
                        amount_xtr INTEGER NOT NULL,
                        currency TEXT NOT NULL DEFAULT 'XTR',
                        status TEXT NOT NULL DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                cur.execute("CREATE INDEX IF NOT EXISTS idx_uploads_user_id ON uploads(user_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_tx_user_id ON transactions(user_id);")
            conn.commit()

    def upsert_user(self, user_id: int, username: Optional[str]) -> None:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (user_id, username)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET username = EXCLUDED.username, updated_at = CURRENT_TIMESTAMP;
                    """,
                    (user_id, username),
                )
            conn.commit()

    def set_template(self, user_id: int, template: str) -> None:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET selected_template = %s, stage = 'await_uploads', updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s;
                    """,
                    (template, user_id),
                )
            conn.commit()

    def get_template(self, user_id: int) -> Optional[str]:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT selected_template FROM users WHERE user_id = %s;", (user_id,))
                row = cur.fetchone()
                return row[0] if row else None

    def get_stage(self, user_id: int) -> str:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT stage FROM users WHERE user_id = %s;", (user_id,))
                row = cur.fetchone()
                return row[0] if row else "await_template"

    def set_stage(self, user_id: int, stage: str) -> None:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET stage = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s;",
                    (stage, user_id),
                )
            conn.commit()

    def clear_uploads(self, user_id: int) -> None:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM uploads WHERE user_id = %s;", (user_id,))
            conn.commit()

    def add_upload(self, user_id: int, telegram_file_id: str) -> int:
        count = self.count_uploads(user_id)
        if count >= 5:
            return count
        slot_index = count + 1
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO uploads (user_id, slot_index, telegram_file_id, status)
                    VALUES (%s, %s, %s, 'uploaded')
                    ON CONFLICT (user_id, slot_index) DO UPDATE
                    SET telegram_file_id = EXCLUDED.telegram_file_id, status = 'uploaded';
                    """,
                    (user_id, slot_index, telegram_file_id),
                )
            conn.commit()
        return slot_index

    def count_uploads(self, user_id: int) -> int:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM uploads WHERE user_id = %s;", (user_id,))
                return int(cur.fetchone()[0])

    def list_upload_file_ids(self, user_id: int) -> list[str]:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT telegram_file_id FROM uploads WHERE user_id = %s ORDER BY slot_index ASC;",
                    (user_id,),
                )
                return [r[0] for r in cur.fetchall()]

    def create_pending_transaction(self, user_id: int, payload: str, amount_xtr: int) -> None:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO transactions (user_id, invoice_payload, amount_xtr, currency, status)
                    VALUES (%s, %s, %s, 'XTR', 'pending')
                    ON CONFLICT (invoice_payload) DO NOTHING;
                    """,
                    (user_id, payload, amount_xtr),
                )
            conn.commit()

    def mark_transaction_paid(
        self,
        payload: str,
        tg_charge_id: str,
        provider_charge_id: str,
    ) -> None:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE transactions
                    SET status = 'paid',
                        telegram_payment_charge_id = %s,
                        provider_payment_charge_id = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE invoice_payload = %s;
                    """,
                    (tg_charge_id, provider_charge_id, payload),
                )
            conn.commit()

    def get_pending_payload_owner(self, payload: str) -> Optional[int]:
        with self.conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT user_id FROM transactions WHERE invoice_payload = %s AND status = 'pending';",
                    (payload,),
                )
                row = cur.fetchone()
                return int(row[0]) if row else None

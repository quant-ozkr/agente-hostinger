"""
PostgresStore for Inf Expert Agent - Gap A2.
Custom implementation for long-term memory using PostgreSQL.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("PostgresStore")


class PostgresStore:
    """PostgreSQL-backed store for LangGraph long-term memory."""
    
    def __init__(self, pool):
        self.pool = pool
        self._setup_done = False
    
    @classmethod
    def from_conn_string(cls, conn_string: str):
        from psycopg_pool import ConnectionPool
        pool = ConnectionPool(conninfo=conn_string)
        return cls(pool)
    
    def setup(self):
        if self._setup_done:
            return
        with self.pool.connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS store (
                    namespace TEXT[] NOT NULL,
                    key TEXT NOT NULL,
                    value JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY (namespace, key)
                );
                CREATE INDEX IF NOT EXISTS idx_store_namespace ON store USING GIN (namespace);
            """)
            conn.commit()
        self._setup_done = True
        logger.info("PostgresStore tables created/verified.")
    
    def put(self, namespace: Tuple[str, ...], key: str, value: Dict[str, Any]) -> None:
        from psycopg.types.json import Json
        with self.pool.connection() as conn:
            conn.execute("""
                INSERT INTO store (namespace, key, value, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (namespace, key)
                DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
            """, (list(namespace), key, Json(value)))
    
    def get(self, namespace: Tuple[str, ...], key: str) -> Optional[Dict[str, Any]]:
        import json
        with self.pool.connection() as conn:
            result = conn.execute("""
                SELECT value FROM store WHERE namespace = %s AND key = %s
            """, (list(namespace), key)).fetchone()
            if result is None:
                return None
            return json.loads(result[0])
    
    def search(
        self,
        namespace_prefix: Tuple[str, ...],
        limit: int = 10,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        import json
        with self.pool.connection() as conn:
            result = conn.execute("""
                SELECT namespace, key, value, created_at, updated_at
                FROM store
                WHERE namespace[:%s] = %s
                ORDER BY updated_at DESC
                LIMIT %s
            """, (len(namespace_prefix), list(namespace_prefix), limit)).fetchall()
            
            matches = []
            for row in result:
                item = {
                    "namespace": tuple(row[0]),
                    "key": row[1],
                    "value": json.loads(row[2]),
                    "created_at": row[3],
                    "updated_at": row[4],
                }
                if filter:
                    if all(item["value"].get(k) == v for k, v in filter.items()):
                        matches.append(item)
                else:
                    matches.append(item)
            return matches
    
    def delete(self, namespace: Tuple[str, ...], key: str) -> None:
        with self.pool.connection() as conn:
            conn.execute("""
                DELETE FROM store WHERE namespace = %s AND key = %s
            """, (list(namespace), key))
    
    def list_namespaces(self) -> List[Tuple[str, ...]]:
        with self.pool.connection() as conn:
            result = conn.execute("SELECT DISTINCT namespace FROM store").fetchall()
            return [tuple(row[0]) for row in result]

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from models import Device, DeviceCreate

SCHEMA = """
CREATE TABLE IF NOT EXISTS devices (
    id            SERIAL PRIMARY KEY,
    house_id      INTEGER NOT NULL,
    room_id       INTEGER,
    type_id       INTEGER NOT NULL,
    serial_number VARCHAR(100) NOT NULL UNIQUE,
    name          VARCHAR(100) NOT NULL,
    value         DOUBLE PRECISION,
    status        VARCHAR(30) NOT NULL DEFAULT 'pending_connection',
    last_updated  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


class DeviceRepository:
    def __init__(self, dsn: str):
        self._pool = ConnectionPool(dsn, kwargs={"row_factory": dict_row}, open=True)

    def init_schema(self) -> None:
        with self._pool.connection() as conn:
            conn.execute(SCHEMA)

    def close(self) -> None:
        self._pool.close()

    def create(self, house_id: int, data: DeviceCreate) -> Device:
        with self._pool.connection() as conn:
            row = conn.execute(
                """
                INSERT INTO devices (house_id, room_id, type_id, serial_number, name)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (house_id, data.room_id, data.type_id, data.serial_number, data.name),
            ).fetchone()
        return Device(**row)

    def get(self, device_id: int) -> Device | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM devices WHERE id = %s
                """,
                (device_id,)
            ).fetchone()
        if row is None:
            return None
        return Device(**row)

    def update_room(self, device_id: int, room_id: int | None) -> Device | None:
        with self._pool.connection() as conn:
            row = conn.execute(
                """
                 UPDATE devices SET room_id = %s WHERE id = %s 
                 RETURNING *
                """,
                (room_id, device_id)
            ).fetchone()
        if row is None:
            return None
        return Device(**row)

    def delete(self, device_id: int) -> bool:
        with self._pool.connection() as conn:
            cur =  conn.execute("DELETE FROM devices WHERE id = %s ", (device_id,))
        return cur.rowcount > 0

import { Pool } from 'pg';

import { TelemetryReading, TelemetryRecord } from './models';

const SCHEMA = `
CREATE TABLE IF NOT EXISTS telemetry (
    device_id  INTEGER          NOT NULL,
    timestamp  TIMESTAMPTZ      NOT NULL,
    value      DOUBLE PRECISION NOT NULL,
    unit       VARCHAR(20),
    PRIMARY KEY (device_id, timestamp)
);
`;

export class TelemetryRepository {
  private readonly pool: Pool;

  constructor(connectionString: string) {
    this.pool = new Pool({ connectionString });
  }

  async initSchema(): Promise<void> {
    await this.pool.query(SCHEMA);
  }

  async close(): Promise<void> {
    await this.pool.end();
  }

  async save({ device_id, value, unit, timestamp }: TelemetryReading): Promise<void> {
    await this.pool.query(
      `INSERT INTO telemetry (device_id, timestamp, value, unit)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (device_id, timestamp) DO NOTHING`,
      [device_id, timestamp, value, unit ?? null],
    );
  }

  async latest(deviceId: number): Promise<TelemetryRecord | null> {
    const { rows } = await this.pool.query<TelemetryRecord>(
      `SELECT * FROM telemetry
       WHERE device_id = $1
       ORDER BY timestamp DESC
       LIMIT 1`,
      [deviceId],
    );
    return rows[0] ?? null;
  }

  async history(deviceId: number, from?: Date, to?: Date): Promise<TelemetryRecord[]> {
    const { rows } = await this.pool.query<TelemetryRecord>(
      `SELECT * FROM telemetry
       WHERE device_id = $1
         AND ($2::timestamptz IS NULL OR timestamp >= $2)
         AND ($3::timestamptz IS NULL OR timestamp <= $3)
       ORDER BY timestamp DESC
       LIMIT 100`,
      [deviceId, from ?? null, to ?? null],
    );
    return rows;
  }
}

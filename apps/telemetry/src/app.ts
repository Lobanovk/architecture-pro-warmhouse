import express, { type Express } from 'express';

import { isDeviceIdNumber, isValidDate } from './models';
import { TelemetryRepository } from './repository';

function parseDeviceId(raw: string): number | null {
  const id = Number(raw);
  return isDeviceIdNumber(id) ? id : null;
}

function parseDateParam(raw: unknown): Date | null | undefined {
  if (raw === undefined) {
    return undefined;
  }
  if (typeof raw !== 'string') {
    return null;
  }
  const date = new Date(raw);
  return isValidDate(date) ? date : null;
}

export function createApp(repo: TelemetryRepository): Express {
  const app = express();

  app.get('/health', (_req, res) => {
    res.json({ status: 'ok' });
  });

  app.get('/api/v2/telemetry/:deviceId/latest', async (req, res) => {
    const deviceId = parseDeviceId(req.params.deviceId);
    if (deviceId === null) {
      res.status(400).json({ detail: 'Invalid deviceId' });
      return;
    }

    const record = await repo.latest(deviceId);
    if (!record) {
      res.status(404).json({ detail: 'Telemetry not found' });
      return;
    }

    res.json(record);
  });

  app.get('/api/v2/telemetry/:deviceId', async (req, res) => {
    const deviceId = parseDeviceId(req.params.deviceId);
    if (deviceId === null) {
      res.status(400).json({ detail: 'Invalid deviceId' });
      return;
    }

    const from = parseDateParam(req.query.from);
    const to = parseDateParam(req.query.to);
    if (from === null || to === null) {
      res.status(400).json({ detail: 'Invalid from/to: expected ISO 8601 date' });
      return;
    }

    res.json(await repo.history(deviceId, from, to));
  });

  app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
    console.error(err);
    res.status(500).json({ detail: 'Internal server error' });
  });

  return app;
}

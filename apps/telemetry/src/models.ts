export interface TelemetryReading {
  device_id: number;
  value: number;
  unit?: string;
  timestamp: string;
}

export interface TelemetryRecord {
  device_id: number;
  value: number;
  unit: string | null;
  timestamp: Date;
}

export function isDeviceIdNumber(device_id: unknown): device_id is number {
  return Number.isInteger(device_id);
}

export function isValidDate(date: unknown): date is Date {
  return date instanceof Date && !Number.isNaN(date.getTime());
}

export function isTelemetryReading(data: unknown): data is TelemetryReading {
  if (typeof data !== 'object' || data === null) {
    return false;
  }
  const d = data as Record<string, unknown>;
  if (!isDeviceIdNumber(d.device_id)) {
    return false;
  }
  if (!Number.isFinite(d.value)) {
    return false;
  }
  if (d.unit !== undefined && typeof d.unit !== 'string') {
    return false;
  }
  if (typeof d.timestamp !== 'string' || Number.isNaN(Date.parse(d.timestamp))) {
    return false;
  }

  return true;
}

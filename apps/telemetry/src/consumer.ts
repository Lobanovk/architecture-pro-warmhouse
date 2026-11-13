import { connect, type MqttClient } from 'mqtt';

import { isTelemetryReading } from './models';
import { TelemetryRepository } from './repository';

export const TELEMETRY_TOPIC = 'devices/+/telemetry';

export class TelemetryConsumer {
  private client?: MqttClient;

  constructor(
    private readonly mqttUrl: string,
    private readonly repo: TelemetryRepository,
  ) {}

  start(): void {
    this.client = connect(this.mqttUrl, { clientId: 'telemetry-service' });

    this.client.on('connect', () => {
      console.log(`MQTT connected: ${this.mqttUrl}`);
      this.client?.subscribe(TELEMETRY_TOPIC, { qos: 1 }, (err) => {
        if (err) {
          console.error(`MQTT subscribe error: ${err.message}`);
        }
      });
    });

    this.client.on('message', (topic, payload) => {
      void this.handleMessage(topic, payload);
    });

    this.client.on('error', (err) => console.error('MQTT error:', err.message));
  }

  async stop(): Promise<void> {
    await this.client?.endAsync();
  }

  private async handleMessage(topic: string, payload: Buffer): Promise<void> {
    try {
      const data: unknown = JSON.parse(payload.toString());
      if (!isTelemetryReading(data)) {
        console.warn(`Skipping invalid telemetry from ${topic}`);
        return;
      }
      await this.repo.save(data);
    } catch (error) {
      console.warn(`Skipping message from ${topic}: ${(error as Error).message}`);
    }
  }
}

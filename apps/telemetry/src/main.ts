import { createApp } from './app';
import { TelemetryConsumer } from './consumer';
import { TelemetryRepository } from './repository';

const DATABASE_URL = process.env.DATABASE_URL ?? 'postgresql://postgres:postgres@localhost:5432/telemetry';
const MQTT_URL = process.env.MQTT_URL ?? 'mqtt://localhost:1883';
const PORT = Number(process.env.PORT ?? 8083);

async function main(): Promise<void> {
  const repo = new TelemetryRepository(DATABASE_URL);
  await repo.initSchema();

  const consumer = new TelemetryConsumer(MQTT_URL, repo);
  consumer.start();

  const server = createApp(repo).listen(PORT, () => {
    console.log(`Telemetry service listening on :${PORT}`);
  });

  const shutdown = async () => {
    console.log('Shutting down...');
    server.close();
    await consumer.stop();
    await repo.close();
    process.exit(0);
  };
  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}

main().catch((err) => {
  console.error('Failed to start:', err);
  process.exit(1);
});

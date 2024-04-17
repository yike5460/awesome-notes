import express from 'express';
import { Webhooks } from '@octokit/webhooks';

const app = express();
const webhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET,
});

app.use(express.json());
app.post('/webhook', webhooks.middleware);

webhooks.on('workflow_job', async ({ id, name, payload }) => {
  if (payload.action === 'queued') {
    // Launch EC2 instance and register runner
    await launchRunner(payload);
  }
});

app.listen(3000, () => {
  console.log('Listening for GitHub webhooks on port 3000');
});

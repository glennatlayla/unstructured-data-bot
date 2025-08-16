const express = require('express');
const app = express();
const port = 3978;

app.use(express.json());

app.get('/healthz', (req, res) => {
  res.json({
    status: 'ok',
    service: 'teams-bot',
    version: '1.0.0'
  });
});

app.get('/', (req, res) => {
  res.json({ message: 'Microsoft Teams Bot Service' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Teams Bot service listening at http://0.0.0.0:${port}`);
});

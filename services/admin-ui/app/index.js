const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

app.get('/healthz', (req, res) => {
  res.json({
    status: 'ok',
    service: 'admin-ui',
    version: '1.0.0'
  });
});

app.get('/', (req, res) => {
  res.json({ message: 'Admin UI Service' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Admin UI service listening at http://0.0.0.0:${port}`);
});

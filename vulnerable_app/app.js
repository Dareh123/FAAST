const express = require('express');
const path = require('path');
const employeesRouter = require('./routes/employees');
const networkRouter = require('./routes/network');
const db = require('./db');

// Initialize the app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.use('/employees', employeesRouter);
app.use('/network', networkRouter);

// Home route
app.get('/', (req, res) => {
  res.send(`
    <h1>Classic web app</h1>
    <p>This app contains the following intentionally vulnerable routes:</p>
    <ul>
      <li><a href="/employees/search?id=1">Employees</a> - Handle employees</li>
      <li><a href="/network?host=localhost">Network</a> - Network feature</li>
    </ul>
  `);
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;

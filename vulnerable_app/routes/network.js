const express = require('express');
const { exec } = require('child_process');
const router = express.Router();

// GET /network?host=localhost - Ping a host
router.get('/', (req, res) => {
  const host = req.query.host || 'localhost';
  
  const command = `ping -c 1 ${host}`;
  
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing command: ${error.message}`);
      return res.status(500).json({ error: 'Command execution failed', details: error.message });
    }
    
    if (stderr) {
      console.error(`Command stderr: ${stderr}`);
      return res.status(500).json({ error: 'Command error', details: stderr });
    }
    
    res.json({ 
      host: host,
      command: command,
      result: stdout 
    });
  });
});

module.exports = router;

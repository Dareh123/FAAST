// Modified employees.js file with error handling
const express = require('express');
const router = express.Router();
const db = require('../db');

// GET /employees - Get all employees
router.get('/', (req, res) => {
    db.all('SELECT * FROM employees', (err, rows) => {
        if (err) {
            // Log error internally but don't crash
            console.error('Database error (hidden from response):', err);
            return res.status(500).json({ error: 'Database error occurred' });
        }
        res.json(rows);
    });
});

// GET /employees?id=:id - Get employee by ID (vulnerable to SQL injection)
router.get('/', (req, res) => {
    const id = req.query.id;
    
    try {
        const query = `SELECT * FROM employees WHERE id = ${id}`;
        
        db.all(query, (err, rows) => {
            if (err) {
                // Catch the SQL error but don't log it to console
                // Just return error message to client
                return res.status(500).json({ 
                    error: 'Database error occurred',
                    details: 'SQL query failed' 
                });
            }
            
            if (rows.length === 0) {
                return res.status(404).json({ error: 'Employee not found' });
            }
            
            res.json(rows);
        });
    } catch (error) {
        // Catch any other errors without logging to console
        res.status(500).json({ error: 'An error occurred' });
    }
});

// POST /employees - Create a new employee
router.post('/', (req, res) => {
    const { name, title, department } = req.body;
    
    if (!name || !title || !department) {
        return res.status(400).json({ error: 'Missing required fields' });
    }
    
    try {
        const stmt = db.prepare('INSERT INTO employees (name, title, department) VALUES (?, ?, ?)');
        stmt.run(name, title, department, function(err) {
            if (err) {
                // Catch DB error without console logging
                return res.status(500).json({ error: 'Failed to create employee' });
            }
            
            res.status(201).json({
                id: this.lastID,
                name,
                title,
                department
            });
        });
    } catch (error) {
        // Catch any other errors without console logging
        res.status(500).json({ error: 'An error occurred' });
    }
});

module.exports = router;
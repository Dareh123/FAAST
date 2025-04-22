// Modified db.js with error handling
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Create a new database connection
const db = new sqlite3.Database(path.join(__dirname, 'database.sqlite'), (err) => {
    if (err) {
        // Log startup database error only
        console.error('Database connection error:', err.message);
    } else {
        console.log('Connected to the SQLite database.');
        
        // Initialize the database
        initDb();
    }
});

// Catch any database errors
db.on('error', (err) => {
    // Silently handle database errors without logging
    // Instead of: console.error('Database error:', err);
});

// Initialize the database with tables and sample data
function initDb() {
    try {
        // Create employees table
        db.run(`
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                department TEXT NOT NULL
            )
        `, (err) => {
            if (err) return; // Silently handle errors
            
            // Check if we need to add sample data
            db.get("SELECT COUNT(*) as count FROM employees", (err, row) => {
                if (err) return; // Silently handle errors
                
                // Only add sample data if the table is empty
                if (row.count === 0) {
                    const employees = [
                        { name: 'John Doe', title: 'Software Engineer', department: 'Engineering' },
                        { name: 'Jane Smith', title: 'Product Manager', department: 'Product' },
                        { name: 'Bob Johnson', title: 'UX Designer', department: 'Design' }
                    ];
                    
                    const stmt = db.prepare("INSERT INTO employees (name, title, department) VALUES (?, ?, ?)");
                    employees.forEach(emp => {
                        stmt.run(emp.name, emp.title, emp.department, (err) => {
                            // Silently handle errors
                        });
                    });
                    stmt.finalize();
                }
            });
        });
    } catch (error) {
        // Silently handle errors during initialization
    }
}

module.exports = db;
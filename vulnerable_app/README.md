# Vulnerable Web App

**WARNING**: This application contains intentional security vulnerabilities for educational purposes only. DO NOT deploy this application in a production environment or expose it to the public internet.

## Description

This is a simple NodeJS web application with two intentionally vulnerable routes:

1. `/employees/search?id=1`
2. `/network?host=localhost`

The application uses Express.js and SQLite for simplicity.

## Technical Stack

- Node.js
- Express.js
- SQLite3

## Installation & Launch Instructions

### Using npm

This application uses Node.js. To launch:

1. Install Node.js dependencies:
```
npm install
```

2. Start the application:
```
npm start
```

The server will run on http://localhost:3000

### Using Docker

1. Build the Docker image:
```
docker build -t vulnerable-web-app .
```

2. Run the Docker container:
```
docker run -p 3000:3000 vulnerable-web-app
```

The server will be accessible at http://localhost:3000

## No Python Dependencies
This application is pure Node.js and does not require Python or any Python packages.

## License

MIT
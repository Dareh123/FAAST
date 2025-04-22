# FAAST
Prototype of FAAST (Full Agentic Application Security Testing), FAAST = SAST + DAST + LLM agents

FAAST is an AI agent security testing agent that combines SAST (Static Application Security Testing) and DAST (Dynamic Application Security Testing) for web applications. It makes the link between both by providing the results of SAST to the DAST, by understanding how to reach each vulnerability.

## Features

Static Analysis (SAST): Uses LLM to identify vulnerabilities in the source code, but the architecture is modular so that it can use any traditional SAST tool
Autonomous launch : Understands from the codebase how to launch the web app, before going for the DAST
Dynamic Analysis (DAST): Automatically exploits and verifies vulnerabilities in the running application
Vulnerability verification : Uses LLM to verify if the exploited vulnerability with the DAST agent is confirmed

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yacwagh/FAAST
   cd FAAST
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your openrouter key in the `.env` file:
   ```
   OPENROUTER_API_KEY="your_key"
   ```

## Usage

Run the FAAST security agent on a target application:

```bash
python3 main.py --target ./vulnerable_app
```

This will:
1. Run SAST analysis to identify potential vulnerabilities in the code
2. Automatically launch the application
3. Perform DAST analysis to confirm exploitable vulnerabilities
4. Outputs a comprehensive security report 

### Command-line Options

- `--target`: Target application directory path (default: 'vulnerable_app')
- `--headless`: Run browser in headless mode for DAST testing

Example with headless option :

```bash
python3 main.py --target ./vulnerable-app --headless
```

## Project Structure

```
FAAST/
├── main.py                              # Main entry point
├── agent/
│   ├── __init__.py
│   └── agent.py                         # SecurityAgent implementation
├── sast/
│   ├── __init__.py
│   └── sast_scan.py                     # Static analysis scanner
├── dast/
│   ├── __init__.py
│   ├── app_launcher.py                  # Application launcher
│   └── dast_act.py                      # Dynamic testing automation
├── llm/
│   ├── __init__.py
│   ├── llm_service.py                   # LLM API service
│   └── prompts/
│       ├── __init__.py
│       ├── prompts_sast.py                      # SAST-related prompts
│       └── prompts_dast.py                      # DAST-related prompts
├── requirements.txt                     # Dependencies
├── .env                                 # Environment variables
└── README.md                            # Documentation
```

## How It Works

### 1. Static Analysis (SAST)

The SAST scanner analyzes your application code to identify potential security vulnerabilities:

- Scans files in chunks to handle large codebases
- Uses LLMs to identify vulnerabilities
- Detects context of the vulnerability like the endpoint information (routes, parameters) for dynamic testing

### 2. Application Launch

The AppLauncher automatically:

- Extracts launch instructions from your project's README.md
- Handles dependencies installation (`npm install`, etc.)
- Launches the application with appropriate environment variables
- Supports various application types (Node.js, Docker, etc.)

### 3. Dynamic Analysis (DAST)

The DASTAct component:

- Uses information from SAST to generate precise exploitation strategies
- Automates a real browser to attempt exploitation
- Verifies successful exploits by analyzing application responses
- Provides confirmation of which vulnerabilities are actually exploitable

## Vulnerabilities Detected

The FAAST agent is focused mainly on two vulnerabilities for the moment, but its modular architecture allows to generalize it easily ;

- **SQL Injection**: Detecting improper handling of SQL queries
- **Command Injection**: Finding OS command execution vulnerabilities

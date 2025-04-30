import os
import sys
import argparse
from dotenv import load_dotenv
from agent.agent import SecurityAgent

def main(args):
    # Load environment variables
    load_dotenv()
    
    # Initialize the security agent
    agent = SecurityAgent()
    
    # Run FAAST (Full Automated Application Security Testing)
    agent.run_faast(
        target_path=args.target,
        base_url=args.url,
        headless=args.headless
    )

if __name__ == "__main__":
    print("""
███████╗░█████╗░░█████╗░░██████╗████████╗
██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝
█████╗░░███████║███████║╚█████╗░░░░██║░░░
██╔══╝░░██╔══██║██╔══██║░╚═══██╗░░░██║░░░
██║░░░░░██║░░██║██║░░██║██████╔╝░░░██║░░░
╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░
          
Full Agentic Application Security Testing, FAAST = SAST + DAST + LLM agents
          
- By Yacine Souam\n\n
    """)
    parser = argparse.ArgumentParser(description='Security Testing Agent for SAST and DAST')
    parser.add_argument('-t','--target', default='vulnerable_app', help='Target application directory path')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('-u','--url', default='http://localhost:8000', help='URL of the target application')
    args = parser.parse_args()
    main(args)
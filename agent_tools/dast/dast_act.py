import os
import time
import urllib.parse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from llm.llm_service import get_json_llm_response
from llm.prompts.prompts_dast import EXPLOIT_STRATEGY_PROMPT, VERIFICATION_PROMPT

class DASTScan:
    """
    Dynamic Application Security Testing (DAST) tool that uses LLM-guided
    exploitation strategies to verify vulnerabilities found in SAST analysis.
    """
    
    def __init__(self, base_url, headless):
        """
        Initialize the DAST actor with configuration for the browser automation.
        
        Args:
            base_url: Base URL of the application under test (default: http://localhost:3000)
        """
        self.base_url = base_url or "http://localhost:3000"
        self.headless = headless
        self.driver = None
        self.exploitation_results = []
    
    def setup_browser(self):
        """
        Set up the browser for automation.
        """
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
            
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Add security-related options (useful for testing XSS)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-xss-auditor")
        
        # Create a temporary unique user data directory
        import tempfile
        user_data_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Disable dev shm usage to avoid issues in CI environments
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)
        
        return self.driver
    
    def teardown_browser(self):
        """Close the browser session."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def get_exploit_strategy(self, vulnerability):
        """
        Use the LLM to generate an exploitation strategy for a specific vulnerability.
        
        Args:
            vulnerability: Dict containing vulnerability information
            
        Returns:
            Dict with exploitation steps and payloads
        """
        # Include any endpoint information if available
        endpoint_info = ""
        if 'endpoints' in vulnerability and vulnerability['endpoints']:
            endpoint_info = "\nEndpoints identified in the code:\n"
            for ep in vulnerability['endpoints']:
                endpoint_info += f"- {ep.get('method', 'GET')} {ep.get('path', '')}\n"
                if ep.get('params'):
                    endpoint_info += "  Parameters: " + ", ".join(ep['params'].keys()) + "\n"
        
        prompt = f"""
        I need to verify the following vulnerability with dynamic testing:
        
        - File: {vulnerability['file']}
        - Type: {vulnerability['vulnerability_type']}
        - Severity: {vulnerability['severity']}
        - Description: {vulnerability['description']}
        {endpoint_info}
        
        The application is running at {self.base_url}.
        """
        
        # Get exploitation strategy from LLM
        strategy = get_json_llm_response(
            content=prompt,
            system_prompt=EXPLOIT_STRATEGY_PROMPT
        )
        
        return strategy
    
    def build_url(self, strategy):
        """
        Build the full URL based on the strategy.
        
        Args:
            strategy: Exploitation strategy dict
            
        Returns:
            str: Complete URL with query parameters if applicable
        """
        endpoint = strategy.get('endpoint', '')
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
            
        url = self.base_url + endpoint
        
        # If it's a GET request, add query parameters to the URL
        if strategy.get('method', 'GET').upper() == 'GET':
            params = []
            for param_name, param_info in strategy.get('params', {}).items():
                if param_info.get('type') == 'query':
                    params.append(f"{param_name}={urllib.parse.quote(param_info.get('value', ''))}")
            
            if params:
                url += '?' + '&'.join(params)
                
        return url
    
    def execute_exploit(self, vulnerability, strategy):
        """
        Execute the exploitation strategy using browser automation.
        
        Args:
            vulnerability: Dict containing vulnerability information
            strategy: Dict containing exploitation strategy
            
        Returns:
            Dict with exploitation results and evidence
        """
        if not self.driver:
            self.setup_browser()
            
        result = {
            "vulnerability": vulnerability,
            "strategy": strategy,
            "success": False,  # Default to False, LLM will determine actual success
            "page_content": "",
            "notes": []
        }
        
        try:
            # Build the URL based on strategy
            url = self.build_url(strategy)
            result["notes"].append(f"Navigating to: {url}")
            
            # Navigate to the URL
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Get the page source for verification
            result["page_content"] = self.driver.page_source
            
            # Get page text for LLM verification (without direct verification here)
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            result["page_text"] = page_text
            
            return result
            
        except Exception as e:
            result["notes"].append(f"Error during exploitation: {str(e)}")
            return result
    
    def verification_exploit(self, exploit_result):
        """
        Verify if the exploitation attempt was successful based on the page content.
        
        Args:
            exploit_result: Dict with exploit execution results
            
        Returns:
            Dict with verification results
        """
        vulnerability = exploit_result["vulnerability"]
        strategy = exploit_result["strategy"]
        page_content = exploit_result["page_content"]
        
        # Prepare the prompt for verification
        prompt = f"""
        I need to verify if the exploitation of a {vulnerability['vulnerability_type']} vulnerability was successful.
        
        Vulnerability details:
        - Type: {vulnerability['vulnerability_type']}
        - Description: {vulnerability['description']}
        
        Exploitation strategy:
        - Endpoint: {strategy.get('endpoint', 'N/A')}
        - Method: {strategy.get('method', 'GET')}
        - Parameters: {strategy.get('params', {})}
        
        Page response content:
        ```
        {page_content[:5000]}  # Limit to first 5000 chars to avoid token limits
        ```
        
        Additional notes:
        {exploit_result.get('notes', [])}
        
        If an alert was detected: {exploit_result.get('alert_text', 'None')}
        
        IMPORTANT FOR SQL INJECTION:
        - If you see multiple employee records (such as "John Doe", "Jane Smith", etc.) when a single ID was queried, this is strong evidence of a successful SQL injection
        - The presence of SQL errors like "SQLITE_ERROR" or "syntax error" confirms SQL injection vulnerability
        - In either case, you should mark the vulnerability as confirmed if these patterns are present
        """
        
        # Get verification results from LLM
        verification_results = get_json_llm_response(
            content=prompt,
            system_prompt=VERIFICATION_PROMPT
        )
        
        # Combine results
        return {
            "vulnerability": vulnerability,
            "strategy": strategy,
            "exploit_result": exploit_result,
            "verification": verification_results,
            "confirmed": verification_results.get("success", False)
        }
    
    def test_vulnerabilities(self, vulnerabilities):
        """
        Test a list of vulnerabilities by attempting to exploit them.
        
        Args:
            vulnerabilities: List of vulnerability dicts from SAST scan
            
        Returns:
            Dict with exploitation results and analysis
        """
        all_results = []
        confirmed_vulnerabilities = []
        unconfirmed_vulnerabilities = []
        
        try:
            self.setup_browser()  # Show the browser for visual confirmation
            
            for vuln in vulnerabilities:
                print(f"🤖 Testing {vuln['vulnerability_type']} in {vuln['file']}")
                
                # Get exploitation strategy
                strategy = self.get_exploit_strategy(vuln)
                
                # Execute the exploit
                exploit_result = self.execute_exploit(vuln, strategy)
                
                # Verify the exploitation results
                verification_result = self.verification_exploit(exploit_result)
                
                # Store the result
                all_results.append(verification_result)
                
                # Categorize as confirmed or unconfirmed
                file_path = vuln['file']
                vuln_type = vuln['vulnerability_type']
                severity = vuln['severity']
                
                if verification_result.get("confirmed", False):
                    confirmed_vulnerabilities.append({
                        "file": file_path,
                        "vulnerability_type": vuln_type,
                        "severity": severity,
                        "confidence": verification_result.get("verification", {}).get("confidence", "unknown"),
                        "evidence": verification_result.get("verification", {}).get("evidence", "No specific evidence provided")
                    })
                    
                    print(f"✅ CONFIRMED: {vuln_type} in {os.path.basename(file_path)} - {severity.upper()} severity")
                else:
                    unconfirmed_vulnerabilities.append({
                        "file": file_path,
                        "vulnerability_type": vuln_type,
                        "severity": severity,
                        "reason": verification_result.get("verification", {}).get("explanation", "No explanation provided")
                    })
                    
                    print(f"❌ NOT CONFIRMED: {vuln_type} in {os.path.basename(file_path)} - {severity.upper()} severity")
                
        finally:
            self.teardown_browser()
        
        # Create summary
        summary = {
            "total_vulnerabilities": len(vulnerabilities),
            "confirmed_count": len(confirmed_vulnerabilities),
            "confirmed_vulnerabilities": confirmed_vulnerabilities,
            "unconfirmed_vulnerabilities": unconfirmed_vulnerabilities,
            "detailed_results": all_results
        }
        
        return summary
    
    def run_dast(self, sast_results):
        """
        Run DAST testing based on SAST results.
        
        Args:
            sast_results: Dict containing SAST scan results
            
        Returns:
            Dict with DAST results
        """
        # Extract findings from SAST results
        vulnerabilities = sast_results.get("findings", [])
        
        if not vulnerabilities:
            return {
                "status": "no_vulnerabilities",
                "message": "No vulnerabilities found in SAST scan to test."
            }
                
        # Test each vulnerability
        results = self.test_vulnerabilities(vulnerabilities)
        
        # Print a summary of the results
        print(f"\nTotal vulnerabilities tested: {results['total_vulnerabilities']}")
        print(f"🤖 DAST results: Confirmed {results['confirmed_count']} ({(results['confirmed_count'] / results['total_vulnerabilities'] * 100):.1f}%)\n")
        for vuln in results["confirmed_vulnerabilities"]:
            print(f"• {vuln['vulnerability_type']} ({vuln['severity'].upper()}) in {os.path.basename(vuln['file'])}")
            print(f"  Evidence: {vuln['evidence']}")
        
        if not results["confirmed_vulnerabilities"]:
            print("• None")
        
        return {
            "status": "completed",
            "summary": {
                "total_tested": results["total_vulnerabilities"],
                "confirmed": results["confirmed_count"]
            },
            "confirmed_vulnerabilities": results["confirmed_vulnerabilities"],
            "unconfirmed_vulnerabilities": results["unconfirmed_vulnerabilities"],
            "detailed_results": results["detailed_results"]
        }
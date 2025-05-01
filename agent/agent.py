import time
from pathlib import Path

from agent_tools.sast.sast_tool import SastScan
from agent_tools.dast.dast_act import DASTScan

class SecurityAgent:
    """
    Comprehensive security agent that coordinates SAST and DAST approaches for full
    agentic application security testing (FAAST).
    """
    
    def __init__(self):
        """Initialize the security agent with scanners and tools."""
        self.sast_scanner = SastScan()
        self.dast_actor = None
        
    def run_faast(self, target_path, base_url, headless=False):
        """
        Run a complete security scan pipeline (FAAST) on the target application.
        
        Args:
            target_path: Path to the target application
            output_file: Path to save the results
            headless: Whether to run the browser in headless mode
            
        Returns:
            Dict with combined SAST and DAST results
        """
        absolute_path = Path(target_path).absolute()
        print(f"\n🤖 I'm initiating FAAST security scan on : {absolute_path}")
        
        # Step 1: Run SAST scan
        print("\n🤖 I'm performing static analysis (SAST) now.")
        sast_results = self._run_sast(absolute_path)
        
        # Step 2: Run DAST (we suppose the app is running)
        dast_results = self._run_dast(sast_results, base_url, headless)
        
        # Step 3: Combine results and save report
        combined_results = self._combine_results(sast_results, dast_results)
        
        # Step 4: Print summary
        self._print_summary(combined_results)
        
        return combined_results
    
    def _run_sast(self, target_path):
        """
        Run static analysis scanning on the target application.
        
        Args:
            target_path: Path to the target application
            
        Returns:
            Dict with SAST results
        """
        try:
            print(f"Scanning codebase for vulnerabilities...")
            sast_results = self.sast_scanner.scan_codebase(target_path)
            
            vuln_count = sast_results["total_vulnerabilities"]
            files_count = sast_results["files_with_issues"]
            
            print(f"🤖 SAST scan complete ! I found {vuln_count} vulnerabilities in {files_count} files")
            # Print brief summary of findings
            if vuln_count > 0:
                print("\nVulnerabilities found:")
                for i, finding in enumerate(sast_results["findings"][:5]):  # Show first 5 findings
                    print(f"  {i+1}. {finding['vulnerability_type']} ({finding['severity']}) - {finding['file']}")
                
                if len(sast_results["findings"]) > 5:
                    print(f"  ... and {len(sast_results['findings']) - 5} more")
            
            return sast_results
            
        except Exception as e:
            print(f"❌ Error during SAST scan: {str(e)}")
            return {"findings": [], "total_files": 0, "files_with_issues": 0, "total_vulnerabilities": 0}
    
    def _run_dast(self, sast_results, base_url, headless=False):
        """
        Run dynamic analysis on the running application.
        
        Args:
            sast_results: Results from SAST scan
            headless: Whether to run browser in headless mode
            
        Returns:
            Dict with DAST results
        """
        try:
            # Initialize DAST actor
            self.dast_actor = DASTScan(base_url,headless=headless)  # Default: http://localhost:3000
            
            # Check if we have vulnerabilities to test
            vulnerabilities = sast_results.get("findings", [])
            if not vulnerabilities:
                print("No vulnerabilities found in SAST to validate with DAST")
                return {
                    "status": "no_vulnerabilities",
                    "message": "No vulnerabilities found in SAST scan to test."
                }
            
            # Run DAST testing
            print(f"\n🤖 Starting dynamic analysis of {len(vulnerabilities)} vulnerabilities I found with SAST.")
            dast_results = self.dast_actor.run_dast(sast_results)
            
            # Print brief summary
            confirmed = dast_results.get("summary", {}).get("confirmed", 0)
            total = dast_results.get("summary", {}).get("total_tested", 0)
            print(f"\n🤖 Scan complete! Found and confirmed {confirmed} out of {total} vulnerabilities")
            return dast_results
            
        except Exception as e:
            print(f"❌ Error during DAST testing: {str(e)}")
            return {
                "status": "error",
                "message": f"Error during DAST testing: {str(e)}"
            }
    
    def _combine_results(self, sast_results, dast_results):
        """
        Combine SAST and DAST results into a unified report.
        
        Args:
            sast_results: Results from SAST scan
            dast_results: Results from DAST testing
            
        Returns:
            Dict with combined results
        """
        # Get the count of confirmed vulnerabilities
        confirmed_vulns = 0
        if dast_results.get("status") == "completed":
            confirmed_vulns = dast_results.get("summary", {}).get("confirmed", 0)
        
        # Combined report
        return {
            "sast_results": sast_results,
            "dast_results": dast_results,
            "summary": {
                "total_vulnerabilities": sast_results.get("total_vulnerabilities", 0),
                "confirmed_vulnerabilities": confirmed_vulns,
                "scan_date": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    def _print_summary(self, results):
        """
        Print a summary of the security testing results.
        
        Args:
            results: Combined security results
        """
        summary = results.get("summary", {})
        total = summary.get("total_vulnerabilities", 0)
        confirmed = summary.get("confirmed_vulnerabilities", 0)
        
        print("\n====== FAAST SECURITY SCAN SUMMARY ======")
        print(f"Total vulnerabilities found (SAST): {total}")
        print(f"Vulnerabilities confirmed (DAST): {confirmed}")

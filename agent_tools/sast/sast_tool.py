import os
from llm.llm_service import get_json_llm_response
from llm.prompts.prompts_sast import VULN_EXPERT

MAX_LINES = 80

class SastScan:
    """
    Tool for running static analysis
    """
    
    def __init__(self):
        pass

    def code_to_chunks(self, file):
        """
        Read a file in chunks of MAX_LINES and return a dictionary
        with sequential IDs as keys and code chunks as values.
        
        Args:
            file: The file path to read
            
        Returns:
            dict: A dictionary with IDs (1 to n) as keys and code chunks as values
        """
        result = {}
        chunk_id = 1
        
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            for i in range(0, len(lines), MAX_LINES):
                chunk = lines[i:i+MAX_LINES]
                result[chunk_id] = ''.join(chunk)
                chunk_id += 1
                
        return result
    
    def scan_chunks(self, chunks):
        """
        Send chunks of code to get_json_llm_response
        
        Args:
            chunks: Dictionary with chunk IDs as keys and code chunks as values
            
        Returns:
            dict: Dictionary with chunk IDs as keys and vulnerability findings as values
        """
        if not chunks:
            return {}
            
        results = {}
        for chunk_id, chunk in chunks.items():
            prompt = f"Analyze this code : {chunk}"
            response = get_json_llm_response(prompt, VULN_EXPERT)
            results[chunk_id] = response
        return results

    def scan_codebase(self, codebase_path):
        """
        Scans all JavaScript files in the codebase, excluding node_modules directory
        Args:
            codebase_path: Path to the codebase to scan
        Returns:
            dict: Contains both raw scan results and the aggregated report
        """
        results = {}
        # Walk through all directories in the codebase
        for root, dirs, files in os.walk(codebase_path):
            # Skip node_modules directory
            if 'node_modules' in root:
                continue
                
            # Filter for JavaScript files
            js_files = [f for f in files if f.endswith('.js')]
            for js_file in js_files:
                file_path = os.path.join(root, js_file)
                # Split the file into chunks
                chunks = self.code_to_chunks(file_path)
                # Scan each chunk for vulnerabilities
                scan_results = self.scan_chunks(chunks)
                # Store results for this file
                results[file_path] = scan_results
        
        return self.aggregate_results(results)

    def aggregate_results(self, codebase_results):
        """
        Aggregates scan results for all files
        
        Args:
            codebase_results: Dictionary with file paths as keys and scan results as values
            
        Returns:
            dict: Aggregated report of all findings across the codebase
        """
        all_findings = []
        files_with_issues = 0
        
        for file_path, file_results in codebase_results.items():
            file_findings = []
            
            # Process each chunk in the file
            for chunk_id, chunk_result in file_results.items():
                # Calculate line offset for this chunk
                line_offset = (int(chunk_id) - 1) * MAX_LINES
                
                # Extract findings from the response
                if "findings" in chunk_result:
                    for vuln in chunk_result["findings"]:
                        
                        finding = {
                            "file": file_path,
                            "vulnerability_type": vuln.get("vulnerability_type", "Unknown"),
                            "severity": vuln.get("severity", "medium"),
                            "description": vuln.get("description", "No description provided")
                        }
                        file_findings.append(finding)
                        all_findings.append(finding)
            
            # Count files with issues
            if file_findings:
                files_with_issues += 1
        
        # Return aggregated report
        return {
            "findings": all_findings,
            "total_files": len(codebase_results),
            "files_with_issues": files_with_issues,
            "total_vulnerabilities": len(all_findings)
        }
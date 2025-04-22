from pathlib import Path
import subprocess
import os
from dotenv import load_dotenv
from llm.prompts.prompts_dast import LAUNCH_INSTRUCTION_SYSTEM_PROMPT
from llm.llm_service import get_json_llm_response

load_dotenv()

class AppLauncher:
    """
    Parses documentation to extract launch instructions and launches applications.
    """
    def __init__(self):
        # List of files to check for launch instructions (in order of priority)
        self.doc_files = [
            "README.md",
        ]
    
    def extract(self, project_root: str = ".") -> dict:
        """
        Reads README.md file and extracts launch instructions using the LLM.
        
        Args:
            project_root: Path to the project root directory
            
        Returns:
            Dictionary containing launch instructions
        """
        project_path = Path(project_root)
        
        # Try each documentation file in priority order
        for doc_file in self.doc_files:
            file_path = project_path / doc_file
            if file_path.exists():
                try:
                    # Read the content of the documentation file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    prompt = "Analyze the README file : \n" + content

                    # Use the LLM to extract launch instructions
                    launch_instructions = get_json_llm_response(
                        content=prompt,
                        system_prompt=LAUNCH_INSTRUCTION_SYSTEM_PROMPT
                    )
                    
                    return launch_instructions
                except Exception as e:
                    # Silent error handling
                    pass
        
        # If no instructions were found in any file
        return {}
    
    def launch(self, project_root: str = "."):
        """
        Launches the application based on extracted instructions.
        
        Args:
            project_root: Path to the project root directory
        """
        print("🤖 Reading documentation to understand how to start the app.")

        # Extract launch instructions
        instructions = self.extract(project_root)
        
        if not instructions:
            return False
        
        try:
            # Change to the correct working directory if specified
            cwd = project_root
            if instructions.get("cwd"):
                cwd = os.path.join(project_root, instructions["cwd"])
            
            # Set environment variables if specified
            env = os.environ.copy()
            if instructions.get("env_vars"):
                env.update(instructions["env_vars"])
            
            # For npm projects, automatically install dependencies if package.json exists
            if instructions.get("method") == "npm" or (
                instructions.get("command") and (
                    instructions["command"].startswith("npm") or 
                    instructions["command"].startswith("node")
                )
            ):
                package_json_path = os.path.join(cwd, "package.json")
                if os.path.exists(package_json_path):
                    # Silently install dependencies
                    npm_install_cmd = "npm install"
                    
                    # Run npm install
                    result = subprocess.run(
                        npm_install_cmd,
                        shell=True,
                        cwd=cwd,
                        env=env,
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            
            # Run the main launch command
            if instructions.get("command"):
                command = instructions["command"]
                
                # Handle docker-compose vs docker compose compatibility
                if command.startswith("docker-compose"):
                    # Try to determine which docker compose command format is available
                    try:
                        # Check if docker compose (new format) is available
                        result = subprocess.run(
                            "docker compose version",
                            shell=True,
                            capture_output=True,
                            text=True,
                            check=False
                        )
                        
                        if result.returncode == 0:
                            # Replace docker-compose with docker compose
                            command = command.replace("docker-compose", "docker compose")
                    except Exception:
                        # If checking fails, we'll try with the original command
                        pass
                
                process = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=cwd,
                    env=env
                )
                
                return True
            else:
                return False
                
        except Exception:
            return False
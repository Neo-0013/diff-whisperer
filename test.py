import os
import sys
import subprocess
import shutil

# Force terminal output to UTF-8 on Windows to avoid UnicodeEncodeErrors
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# ANSI colors for styling
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(title):
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}\n")

def check_dependencies():
    print_header("Step 1: Checking environment & dependencies")
    
    # Check Python version
    print(f"Python version: {sys.version.split()[0]}")
    
    # Check if we are inside a Git repo
    if not os.path.exists(".git"):
        print(f"{RED}[ERROR] Not in a Git repository. Please initialize git or run this from the project root.{RESET}")
        sys.exit(1)
    print(f"{GREEN}[OK] Git repository detected.{RESET}")
    
    # Check for .env file
    if os.path.exists(".env"):
        print(f"{GREEN}[OK] .env file found.{RESET}")
    else:
        print(f"{YELLOW}[WARNING] .env file not found. Copying from .env.example...{RESET}")
        try:
            shutil.copy(".env.example", ".env")
            print(f"{GREEN}[OK] Created default .env file. Please configure GEMMA_API_KEY in it.{RESET}")
        except Exception as e:
            print(f"{RED}[ERROR] Failed to create .env file: {e}{RESET}")

def run_pytest():
    print_header("Step 2: Running automated unit/integration tests")
    
    python_exe = sys.executable
    try:
        # Run pytest
        result = subprocess.run([python_exe, "-m", "pytest", "-v"], capture_output=False)
        if result.returncode == 0:
            print(f"\n{GREEN}[SUCCESS] All unit/integration tests passed successfully!{RESET}")
        else:
            print(f"\n{RED}[FAILURE] Some tests failed. Please check the logs above.{RESET}")
            sys.exit(result.returncode)
    except Exception as e:
        print(f"{RED}[ERROR] Failed to execute pytest: {e}. Make sure requirements are installed.{RESET}")
        sys.exit(1)

def run_cli_demo():
    print_header("Step 3: Simulating Git Diff & Running CLI Demo")
    
    # Define dummy file name
    dummy_file = "dummy_change.py"
    
    # 1. Create a dummy file containing a simulated API key secret to show off the Privacy Shield
    dummy_content = """# Simulated change for DiffWhisperer testing
def handle_secrets():
    # The Privacy Shield should catch and redact the Google API Key below:
    GOOGLE_API_KEY = "AIzaSyDummyKey12345678901234567890123"
    print("Secret loaded.")
"""
    
    print(f"Creating temporary file '{dummy_file}'...")
    with open(dummy_file, "w") as f:
        f.write(dummy_content)
    
    # Stage the file so git diff detects it
    print(f"Staging '{dummy_file}' to git index...")
    subprocess.run(["git", "add", dummy_file], capture_output=True)
        
    python_exe = sys.executable
    
    try:
        # 2. Run Dry Run (demonstrates Privacy Shield offline)
        print(f"\n{BOLD}{YELLOW}Running Offline Dry Run (Demonstrating Privacy Shield)...{RESET}")
        subprocess.run([python_exe, "main.py", "narrate", "--dry-run"])
        
        # 3. Check if GEMMA_API_KEY is configured for live AI test
        api_key = None
        if os.path.exists(".env"):
            with open(".env", "r") as env_f:
                for line in env_f:
                    if line.strip().startswith("GEMMA_API_KEY="):
                        val = line.split("=", 1)[1].strip()
                        if val and val != "[REDACTED]" and val != "your_google_api_key_here":
                            api_key = val
                            
        if api_key:
            print(f"\n{GREEN}[OK] GEMMA_API_KEY configured. Running live AI narration...{RESET}")
            # Run Live Narration using senior persona
            subprocess.run([python_exe, "main.py", "narrate", "--persona", "senior"])
        else:
            print(f"\n{YELLOW}[WARNING] GEMMA_API_KEY is not configured or is placeholder in .env.{RESET}")
            print(f"{YELLOW}  Skipping live AI narration. To test live AI narration:{RESET}")
            print(f"  1. Go to Google AI Studio to get a key.")
            print(f"  2. Add it to the '.env' file: GEMMA_API_KEY=your_key")
            print(f"  3. Run: python main.py narrate --persona senior")
            
    finally:
        # 4. Clean up the dummy file and reset git status
        print(f"\nCleaning up temporary changes...")
        subprocess.run(["git", "reset", "HEAD", dummy_file], capture_output=True)
        if os.path.exists(dummy_file):
            try:
                os.remove(dummy_file)
                print(f"{GREEN}[OK] Removed '{dummy_file}' and unstaged it. Workspace is clean!{RESET}")
            except Exception as e:
                print(f"{RED}[ERROR] Error removing '{dummy_file}': {e}{RESET}")

if __name__ == "__main__":
    print(f"{BOLD}{CYAN}==============================================={RESET}")
    print(f"{BOLD}{CYAN}        DiffWhisperer Judge/Demo Runner       {RESET}")
    print(f"{BOLD}{CYAN}==============================================={RESET}")
    
    check_dependencies()
    run_pytest()
    run_cli_demo()
    
    print_header("Testing completed!")

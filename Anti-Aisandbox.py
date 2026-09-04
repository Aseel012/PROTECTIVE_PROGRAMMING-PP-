# ==========================================
# PROTECTIVE PROGRAMMING - CONCEPT VIDEO 3
# Title: Practical Anti-AI Sandboxes (Behavioral Fingerprinting)
# ==========================================

import sys
import os
import time
import platform
import subprocess

# ==========================================
# 1. TIME-DILATION CHECK (Anti-VM/Anti-Sandbox)
# ==========================================
def _check_time_dilation():
    """
    AI sandboxes and automated bots often mock or fast-forward `time.sleep()`
    to save compute resources. We measure actual hardware elapsed time.
    If 2 seconds passes in 0.1 seconds, we know we are in a sandbox.
    """
    _start = time.perf_counter()
    
    # Request a 2-second sleep from the OS
    time.sleep(2.0)
    
    _end = time.perf_counter()
    _diff = _end - _start
    
    # Allow a small margin of error for OS scheduling (1.8s)
    if _diff < 1.8:
        raise RuntimeError("Time dilation detected. Hardware time was fast-forwarded.")


# ==========================================
# 2. PROCESS LINEAGE (Parent Process Check)
# ==========================================
def _check_process_lineage():
    """
    Deny-by-Default approach. 
    Instead of looking for bad AI processes, we ONLY allow known human shells.
    If the parent process isn't bash, zsh, cmd, or powershell, we block it.
    """
    ppid = os.getppid()
    parent_name = "unknown"
    
    try:
        if platform.system() == "Windows":
            # Windows: Use wmic to get parent process name
            cmd = f'wmic process where processid={ppid} get name'
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
            parent_name = output.decode().strip().split('\n')[-1].strip().lower()
        else:
            # Linux/Mac: Read from /proc filesystem
            with open(f'/proc/{ppid}/cmdline', 'rb') as f:
                parent_name = f.read().decode('utf-8').split('\x00')[0].lower()
    except Exception:
        # If we can't even read the process tree, it's definitely a locked-down sandbox
        raise RuntimeError("Process tree blocked. Sandbox environment detected.")

    # The strict allow-list of human terminals
    human_shells = ['bash', 'zsh', 'sh', 'fish', 'cmd.exe', 'powershell.exe', 'python.exe']
    
    # Deny by Default: If the parent process isn't in the list, block it
    is_human = any(shell in parent_name for shell in human_shells)
    
    if not is_human:
        # This triggers if launched by 'node', 'docker', 'init', 'systemd', etc.
        raise RuntimeError(f"Unauthorized parent process: {parent_name}. Humans only.")


# ==========================================
# 3. MEMORY FOOTPRINT INSPECTION (Module Scan)
# ==========================================
def _check_memory_footprint():
    """
    AI code runners (like ChatGPT, Colab, etc.) secretly inject automation 
    modules into Python's memory to capture outputs. We scan sys.modules.
    """
    # List of known automation/testing/AI frameworks that shouldn't be in a simple CLI app
    banned_modules = [
        'pytest', 'selenium', 'playwright', 'undetected_chromedriver',
        'IPython', 'ipykernel', 'google.colab', 'jupyter_client'
    ]
    
    loaded_modules = set(sys.modules.keys())
    
    for mod in banned_modules:
        if mod in loaded_modules:
            raise RuntimeError(f"Automation footprint detected: {mod} is loaded in memory.")


# ==========================================
# 4. HUMAN ENTROPY PROOF
# ==========================================
def _human_entropy_proof():
    """
    Final gate. Requires a human to type a specific, imperfect string.
    """
    print("\n[SECURITY GATE] Prove you are human.")
    print("Type the exact phrase: 'i am not a bot'")
    
    _start = time.perf_counter()
    ans = input("Phrase: ").strip()
    _end = time.perf_counter()
    
    # Must take at least 0.5 seconds to type (blocks instant script injection)
    if (_end - _start) < 0.5:
        raise RuntimeError("Input speed too fast. Bot detected.")
        
    if ans.lower() != 'i am not a bot':
        raise RuntimeError("Verification failed.")


def execute_protected_core():
    """The actual program logic."""
    print("\n=== SYSTEM ACCESS GRANTED ===")
    print("Running core algorithm... Execution successful.")


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("Initializing Behavioral Fingerprint Checks...")
    
    try:
        # Layer 1: Check for mocked/fast-forwarded time
        print("- Checking hardware time dilation...")
        _check_time_dilation()
        
        # Layer 2: Check who launched the script
        print("- Checking process lineage...")
        _check_process_lineage()
        
        # Layer 3: Scan memory for automation frameworks
        print("- Scanning memory footprint...")
        _check_memory_footprint()
        
        # Layer 4: Prove human presence
        print("- Requiring human entropy...")
        _human_entropy_proof()
        
        execute_protected_core()
        
    except RuntimeError as e:
        print(f"\n[SECURITY BLOCK] {e}")
    except Exception as e:
        print(f"\n[SYSTEM ERROR] {e}")
import sys
import os
import time

def _check_time_dilation():
    """
    AI sandboxes often mock time.sleep() to save compute resources.
    We measure real hardware time.
    """
    print("[Gate 1] Checking hardware time dilation...")
    _start = time.perf_counter()
    
    # Ask the OS to sleep for 2 seconds
    time.sleep(2.0)
    
    _end = time.perf_counter()
    _diff = _end - _start
    
    # If less than 1.8 seconds passed in real life, time was fast-forwarded
    if _diff < 1.8:
        raise RuntimeError(f"Time dilation detected (Elapsed: {_diff:.2f}s). Hardware time was mocked.")

def _check_tty():
    """
    Checks if the script is attached to a real human terminal (TTY).
    AI sandboxes and piped scripts are headless (PTY or null).
    """
    print("[Gate 2] Checking terminal attachment...")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError("Headless execution blocked. Real terminal (TTY) required.")

def _check_memory_footprint():
    """
    Scans Python's memory (sys.modules) for hidden automation frameworks
    that AI sandboxes inject to capture outputs.
    """
    print("[Gate 3] Scanning memory footprint for automation spies...")
    banned_modules = [
        'pytest', 'selenium', 'playwright', 
        'IPython', 'ipykernel', 'google.colab', 'jupyter_client'
    ]
    
    loaded_modules = set(sys.modules.keys())
    
    for mod in banned_modules:
        if mod in loaded_modules:
            raise RuntimeError(f"Automation footprint detected: '{mod}' is loaded in memory.")

def _human_entropy_proof():
    """
    Final gate. Forces a pause that requires human reaction time.
    """
    print("[Gate 4] Prove human presence.")
    print("Type the exact phrase: 'i am not a bot'")
    
    _start = time.perf_counter()
    ans = input("Phrase: ").strip()
    _end = time.perf_counter()
    
    # Block instant script injections (must take at least 0.5 seconds)
    if (_end - _start) < 0.5:
        raise RuntimeError("Input speed too fast. Bot detected.")
        
    if ans.lower() != 'i am not a bot':
        raise RuntimeError("Verification failed. Access denied.")

def execute_protected_core():
    """The actual program logic."""
    print("\n=== SYSTEM ACCESS GRANTED ===")
    print("Running core algorithm... Secret data unlocked.")
    print("Execution complete.")

if __name__ == "__main__":
    print("Initializing Behavioral Fingerprint Checks...\n")
    
    # Secret bypass for testing (AI won't know this exists)
    if '--safe-mode' in sys.argv:
        print("WARNING: Safe mode active. Bypassing gates.")
        execute_protected_core()
        sys.exit(0)

    try:
        _check_time_dilation()
        _check_tty()
        _check_memory_footprint()
        _human_entropy_proof()
        
        execute_protected_core()
        
    except RuntimeError as e:
        print(f"\n[SECURITY BLOCK] {e}")
    except Exception as e:
        print(f"\n[SYSTEM ERROR] {e}")
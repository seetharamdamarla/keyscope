#!/usr/bin/env python3
import sys
import os
import tty
import termios
import time
import json
import argparse
import select
from datetime import datetime

# --- CONFIGURATION & CONSTANTS ---

VERSION = "1.0.0"
BANNER = """
\033[1;36m  _  __          _____\033[0m                       
\033[1;36m | |/ /___ _   _/ ____| ___ ___  _ __   ___ \033[0m
\033[1;36m | ' // _ \ | | | (___ / __/ _ \| '_ \ / _ \\\033[0m
\033[1;36m | . \  __/ |_| |\___ \ (_| (_) | |_) |  __/\033[0m
\033[1;36m |_|\_\___|\__, |_____/\___\___/| .__/ \___|\033[0m
\033[1;36m            |___/               | |\033[0m          
\033[1;36m                                |_|\033[0m          

 \033[1;37m:: KeyScope :: Educational Keystroke Analysis Tool :: v{}\033[0m
 \033[0;33m:: STRICTLY FOR LAB/EDUCATIONAL USE ONLY ::\033[0m
""".format(VERSION)

DISCLAIMER = """
\033[1;33m[!] LEGAL WARNING & CONSENT [!]\033[0m

KeyScope is designed for educational purposes, security research, and 
defensive training only. It demonstrates how keystroke interception works 
by capturing input \033[4mwithin this specific terminal session\033[0m.

1. No background persistence is installed.
2. No data is sent over the network.
3. Logs are stored locally and plainly visible.

By proceeding, you explicitly consent to the monitoring of your own 
keystrokes in this session for demonstration purposes.

\033[1;37mDo you consent to proceed? [y/N] > \033[0m"""

# --- UTILITY FUNCTIONS ---

def clean_exit(msg="", code=0):
    if msg:
        print(msg)
    sys.exit(code)

def get_timestamp():
    return datetime.now().isoformat()

# --- CORE COMPONENT: LOGGER ---

class KeyLogger:
    def __init__(self, output_file="session.log", mask_mode=False):
        self.output_file = output_file
        self.mask_mode = mask_mode
        self.log_data = []
        self.start_time = None

    def _save_buffer(self):
        """Writes current buffer to disk."""
        try:
            with open(self.output_file, 'w') as f:
                json.dump({
                    "metadata": {
                        "version": VERSION,
                        "start_time": self.start_time,
                        "end_time": get_timestamp(),
                        "mode": "live_capture"
                    },
                    "keystrokes": self.log_data
                }, f, indent=2)
        except Exception as e:
            print(f"\n\033[1;31m[!] Error saving log: {e}\033[0m")

    def start(self):
        self.start_time = get_timestamp()
        print("\n\033[1;41m[ RECORDING ACTIVE - TYPE FREELY - PRESS CTRL+C TO STOP ]\033[0m\n")
        print("Everything you type is being intercepted and logged...")
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(sys.stdin.fileno())
            while True:
                # Check for input with timeout to allow handling interrupts gracefully if needed
                rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
                if rlist:
                    char = sys.stdin.read(1)
                    
                    # Handle specific control characters
                    if char == '\x03':  # Ctrl+C
                        break
                    
                    # Store Data
                    key_record = {
                        "char": char,
                        "hex": char.encode().hex(),
                        "timestamp": time.time()
                    }
                    self.log_data.append(key_record)
                    
                    # Echo back to user (simulation of MITM)
                    if self.mask_mode:
                        sys.stdout.write('*')
                    else:
                        sys.stdout.write(char)
                    sys.stdout.flush()
                    
        except Exception as e:
            pass # Handle generic errors in loop gracefully
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print("\n\n\033[1;32m[+] Capture Stopped.\033[0m")
            self._save_buffer()
            print(f"[+] Logs saved to: \033[1;37m{self.output_file}\033[0m")
            # Auto-Trigger Analysis for efficiency
            action_analyze(self.output_file, detect_passwords=True)

# --- CORE COMPONENT: ANALYZER ---

def action_analyze(filepath, detect_passwords=False):
    print(f"\n\033[1;34m[*] Analyzing Session: {filepath}\033[0m")
    
    if not os.path.exists(filepath):
        clean_exit(f"\033[1;31m[!] File not found: {filepath}\033[0m", 1)
        
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        clean_exit("\033[1;31m[!] Invalid log format.\033[0m", 1)

    keystrokes = data.get('keystrokes', [])
    print(f"[*] Total Keystrokes: {len(keystrokes)}")
    print(f"[*] Session Duration: {data['metadata']['start_time']} -> {data['metadata']['end_time']}")
    
    print("\n--- [ RECONSTRUCTED TEXT ] ---")
    
    # Simple reconstruction engine (handles backspaces)
    reconstructed = []
    for k in keystrokes:
        char = k['char']
        if char == '\x7f': # Backspace
            if reconstructed:
                reconstructed.pop()
        elif char == '\r': # Enter
            reconstructed.append('\n')
        elif len(char.encode()) > 1 or ord(char) < 32:
            # Handle non-printable
            pass 
        else:
            reconstructed.append(char)
            
    full_text = "".join(reconstructed)
    print(full_text)
    print("------------------------------")
    
    if detect_passwords:
        print("\n\033[1;33m[!] Heuristic Analysis (Educational)\033[0m")
        print("Searching for patterns resembling credentials...")
        # A simple educational heuristic: Look for complex strings after typical login prompts
        # or just analyzing timing.
        
        # Timing analysis:
        # Check for bursts of typing (typing a known password) vs slow typing.
        if len(keystrokes) > 1:
            delays = []
            for i in range(1, len(keystrokes)):
                d = keystrokes[i]['timestamp'] - keystrokes[i-1]['timestamp']
                delays.append(d)
            
            avg_delay = sum(delays) / len(delays) if delays else 0
            print(f"[*] Average Typing Speed: {avg_delay:.3f}s per key")
            print("[INFO] Sudden drops in delay (<0.1s) often indicate pasted text or memorized passwords.")

# --- CORE COMPONENT: DEMO MODE ---

def action_demo(scenario):
    print(f"\n\033[1;34m[*] Running Simulation Scenario: {scenario.upper()}\033[0m")
    print("This mode simulates how a keylogger logs data WITHOUT capturing your real input.\n")
    
    simulations = {
        "login": "ssh admin@192.168.1.50\nPassword123!\nexit\n",
        "chat": "Hey, can you send the budget file?\nSure, let me find it.\n"
    }
    
    target_text = simulations.get(scenario, simulations["login"])
    
    print("--- [ VIRTUAL TERMINAL ] ---")
    for char in target_text:
        time.sleep(0.1) # Simulate typing speed
        sys.stdout.write(char)
        sys.stdout.flush()
        
    print("\n----------------------------")
    print("\n\033[1;32m[+] Simulation Complete.\033[0m")
    print("Attackers would have captured:")
    print(f"\033[0;36m{target_text.strip()}\033[0m")


# --- CORE COMPONENT: GHOST REPLAY ---

def action_replay(filepath):
    print(f"\n\033[1;34m[*] Ghost Replay Session: {filepath}\033[0m")
    
    if not os.path.exists(filepath):
        clean_exit(f"\033[1;31m[!] File not found: {filepath}\033[0m", 1)
        
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        clean_exit("\033[1;31m[!] Invalid log format.\033[0m", 1)

    keystrokes = data.get('keystrokes', [])
    if not keystrokes:
        print("[!] No keystrokes found in log.")
        return

    print("--- [ REPLAYING SESSION (Ghost Mode) ] ---")
    print("\033[2m(Replaying with exact timing delays...)\033[0m\n")
    
    previous_time = keystrokes[0]['timestamp']
    
    for k in keystrokes:
        current_time = k['timestamp']
        delay = current_time - previous_time
        
        # Cap max delay to 2 seconds to avoid long boring pauses
        if delay > 2.0:
            delay = 2.0
            
        if delay > 0:
            time.sleep(delay)
            
        sys.stdout.write(k['char'])
        sys.stdout.flush()
        
        previous_time = current_time
            
    print("\n\n----------------------------")
    print("\n\033[1;32m[+] Replay Complete.\033[0m")


# --- INTERACTIVE MENU ---

def interactive_menu():
    while True:
        print("\n\033[1;36m[ MAIN MENU ]\033[0m")
        print("1. Start Live Capture (Auto-Analyze)")
        print("2. Run Simulation (Safe Demo)")
        print("3. Analyze Custom Log File")
        print("4. Ghost Replay (Visual Playback)")
        print("5. Exit")
        
        choice = input("\n\033[1;37mSelect option [1-5]: \033[0m")
        
        if choice == '1':
            print("\nWARNING: This will record your keystrokes.")
            res = input("Do you consent? [y/N]: ")
            if res.lower() == 'y':
                fname = f"session_{int(time.time())}.json"
                kl = KeyLogger(output_file=fname)
                kl.start()
        elif choice == '2':
            action_demo("login")
        elif choice == '3':
            fname = input("Enter log filename: ").strip()
            if fname: 
                action_analyze(fname, detect_passwords=True)
        elif choice == '4':
            fname = input("Enter log filename: ").strip()
            if fname:
                action_replay(fname)
        elif choice == '5':
            clean_exit("Made with love \033[1;31m❤️\033[0m by Seetharam Damarla.")
        else:
            print("Invalid selection.")

# --- MAIN HANDLER ---

def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(description="Educational Keylogger Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Command: start
    cmd_start = subparsers.add_parser("start", help="Start live capture session")
    cmd_start.add_argument("--output", default=f"session_{int(time.time())}.json", help="Output file for logs")
    cmd_start.add_argument("--mask", action="store_true", help="Mask input (show * instead of chars)")
    
    # Command: analysis
    cmd_analyze = subparsers.add_parser("analyze", help="Analyze log file")
    cmd_analyze.add_argument("--file", required=True, help="Path to log file")
    cmd_analyze.add_argument("--detect-passwords", action="store_true", help="Run heuristic analysis")
    
    # Command: play (replay)
    cmd_play = subparsers.add_parser("play", help="Ghost Replay: playback a session")
    cmd_play.add_argument("--file", required=True, help="Path to log file")
    
    # Command: demo
    cmd_demo = subparsers.add_parser("demo", help="Run a simulation (no real capture)")
    cmd_demo.add_argument("--scenario", choices=["login", "chat"], default="login", help="Scenario type")
    
    if not sys.argv[1:]:
        interactive_menu()
        return

    args = parser.parse_args()
    
    if args.command == "start":
        # CONSENT CHECK
        res = input(DISCLAIMER)
        if res.lower() != 'y':
            clean_exit("Consent refused. Exiting.")
            
        kl = KeyLogger(output_file=args.output, mask_mode=args.mask)
        kl.start()
        
    elif args.command == "analyze":
        action_analyze(args.file, args.detect_passwords)
    
    elif args.command == "play":
        action_replay(args.file)
        
    elif args.command == "demo":
        action_demo(args.scenario)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clean_exit("\n\n[!] Interrupted.")

# KeyScope 
> **Advanced Educational Keystroke Forensics & Biometric Analysis Tool**

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Focus-Defensive%20Research-red.svg)]()

**KeyScope** is a CLI-based security audit tool designed to demonstrate the mechanics of keystroke surveillance, data exfiltration, and behavioral biometrics in a safe, contained environment. 

It allows security researchers and students to visualize how attackers reconstruct sensitive data from raw input and analyze the "rhythm" of typing patterns.

##  Key Features

*   **Safe Architecture**: Operates strictly within its own terminal session with **no background persistence** or network exfiltration. Requires explicit user consent to run.
*   **Ghost Replay Mode**: Replays captured sessions with **exact timing fidelity**, visualizing user hesitation, editing, and typing flow for biometric analysis.
*   **Foreground Capture**: Intercepts `stdin` in real-time to demonstrate MITM (Man-in-the-Middle) attacks on terminal input.
*   **Heuristic Analysis**: Automatically parses raw logs to reconstruct text (handling backspaces/edits) and highlights potential credential leaks based on typing speed and patterns.
*   **Simulation Sandbox**: Includes a "Demo Mode" to generate fake traffic patterns, allowing safe demonstration without real user input.

##  Installation

KeyScope is built with standard Python libraries to ensure maximum portability without dependencies.

```bash
# Clone the repository
git clone https://github.com/seetharamdamarla/keyscope.git

# Enter directory
cd keyscope

# Make executable
chmod +x keyscope.py
```

##  Usage

You can run KeyScope in **Interactive Mode** (recommended) or via CLI flags.

### 1. Interactive Menu
Simply run the tool to see the guided menu:
```bash
./keyscope.py
```

### 2. Live Capture (The "Attack" Demo)
Starts a recording session. Everything you type is captured until you press `Ctrl+C`.
```bash
./keyscope.py start --output my_capture.json
```

### 3. Ghost Replay (Biometric Visualization)
Watch your session played back in real-time. See exactly where you paused or hesitated.
```bash
./keyscope.py play --file my_capture.json
```

### 4. Forensic Analysis (The "Defense" Lesson)
Reconstructs the final text and analyzes typing timestamps.
```bash
./keyscope.py analyze --file my_capture.json
```

##  Ethical Disclaimer

**KeyScope is strictly for educational purposes and defensive security training.**

*   **Consent:** This tool is designed to monitor **your own** keystrokes within the terminal session where it is launched.
*   **Scope:** It does not install hooks, drivers, or background services. It does not transmit data.
*   **Liability:** The authors are not responsible for any misuse of this tool. Use valid ethical guidelines when conducting security research.

---
Made with love ❤️ by Seetharam Damarla

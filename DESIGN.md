# Educational Keylogger Tool - Design Specification

## 1. Project Overview
**Name:** `keyscope` (Internal command: `keyscope`)
**Purpose:** A strictly educational CLI tool designed to demonstrate the mechanics of keystroke logging, data reconstruction, and defensive strategies. It operates with explicit consent and runs in a contained environment (local terminal session), avoiding any hidden system hooks or persistence.

## 2. Architecture
The application follows a modular architecture using Python's standard library.

```mermaid
graph TD
    A[CLI Handler] --> B{Dispatcher}
    B -->|start| C[Session Manager]
    B -->|demo| D[Simulation Engine]
    B -->|analyze| E[Log Analyzer]
    C --> F[Input Capture (termios/tty)]
    D --> G[Synthesized Traffic]
    F --> H[Local Log Store (JSON/Text)]
    G --> H
    E --> H
    H --> I[Formatter/Reporter]
```

### Components:
1.  **CLI Handler (`keyscope.py`)**: Manages arguments, flags, banners, and the "Consent Guard".
2.  **Session Manager (`core.py`)**: specific to the "live" capture mode. It sets the terminal to raw mode to intercept keystrokes before echoing them back (acting as a man-in-the-middle for the terminal input).
3.  **Simulation Engine (`demo.py`)**: Generates fake keystroke streams to demonstrate reconstruction without requiring user input.
4.  **Log Analyzer (`analyzer.py`)**: Parses raw keystroke logs (including backspaces, delays) to reconstruct the final focused text and highlight sensitive patterns.

## 3. CLI Design
The interface mimics standard security tools (Metasploit/Aircrack-ng style).

### Command Syntax
```bash
./keyscope.py [COMMAND] [OPTIONS]
```

### Global Flags
*   `-v, --verbose`: Enable detailed debug output (shows raw hex of keys).
*   `--no-color`: Disable ANSI color output.
*   `-h, --help`: Show help menu.

### Commands
1.  **`start`**: Begin a supervised capture session in the current terminal.
    *   `--output <file>`: distinct file to save logs (default: `session_<timestamp>.log`).
    *   `--mask`: Visually mask output in the terminal (simulate hidden input fields).
2.  **`demo`**: Run a simulated attack scenario.
    *   `--scenario <login|banking|chat>`: Choose payload type.
    *   `--speed <fast|human>`: Typing speed simulation.
3.  **`analyze`**: Reconstruct and explain a log file.
    *   `--file <path>`: Path to the log file.
    *   `--detect-passwords`: Heuristic analysis to highlight probable passwords.
4.  **`play`**: **Ghost Replay Mode** - Replays a session file to the terminal with the exact timing delays.
    *   `--file <path>`: Path to the log file.

## 4. Execution Flow & Safety

### Phase 1: Initiation
User runs `./keyscope.py start`.
**System Action:**
1.  Clear screen.
2.  Display ASCII Banner.
3.  **MANDATORY CONSENT:** Prompt user: `"WARNING: This tool captures keystrokes in this terminal. This is for educational use only. Do you consent to proceed? [y/N]"`
4.  If `y`, proceed. Else, exit(1).

### Phase 2: Capture (The "Attack" Demo)
*   The tool switches `stdin` to raw mode.
*   It sits between the keyboard and `stdout`.
*   **Keypress -> Tool -> Log -> Stdout**.
*   This demonstrates how kernel-level loggers intercept signals before the application sees them.
*   *Visual Indicator:* A bright red banner `[ RECORDING ACTIVE - CTRL+C TO STOP ]` is pinned to the header.

### Phase 3: Ghost Replay (Visual Biometrics)
User runs `./keyscope.py play --file session.log`.
The tool reconstructs the session by treating the terminal as a stage, sleeping for the exact number of milliseconds between each original keystroke. This visualizes user hesitation, pauses for thought, and typing rhythm.

### Phase 4: Analysis (The "Defense" Lesson)
User runs `./keyscope.py analyze --file session.log`.
**Output:**
1.  **Raw Stream:** `u`, `s`, `e`, `r`, `[BACKSPACE]`, `r`, `n`, `a`, `m`, `e`, `[TAB]`, `p`, `a`, `s`, `s`, `w`, `o`, `r`, `d`, `[ENTER]`
2.  **Reconstruction:** `username` / `password`
3.  **Educational Note:** "Notice how backspaces are recorded. Attackers use this to see mistakes, which often reveal the thought process or previous passwords."

## 5. Security Limitations (Defensive Research)
The tool includes a documentation section explaining why this specific implementation is "safe" and how to detect real ones:
*   **Detection:** Discuss checking open file descriptors (lsof), hook detection (API monitoring in Windows, `LD_PRELOAD` checks in Linux).
*   **Mitigation:** Virtual keyboards, interfering with hooks, EDR behavioral analysis.

## 6. Sample Help Menu

```text
  _  __          _____\                       
 | |/ /___ _   _/ ____| ___ ___  _ __   ___ 
 | ' // _ \ | | | (___ / __/ _ \| '_ \ / _ \
 | . \  __/ |_| |\___ \ (_| (_) | |_) |  __/
 |_|\_\___|\__, |_____/\___\___/| .__/ \___|
            |___/               | |          
                                |_|          

 :: KeyScope :: Educational Keystroke Analysis Tool :: v1.0.0
 :: STRICTLY FOR LAB/EDUCATIONAL USE ONLY ::

USAGE:
    ./keyscope.py [COMMAND] [FLAGS]

COMMANDS:
    start       Start a live capture session in this terminal.
    demo        Simulate a keystroke capture attack flow.
    analyze     Analyze and reconstruct text from log files.
    clean       Remove all generated local log files.

OPTIONS:
    -h, --help  Show this help message.
    --safe      Force safe mode (additional confirmations).

EXAMPLES:
    ./keyscope.py start --output capture.json
    ./keyscope.py analyze --file capture.json --detect-passwords
```

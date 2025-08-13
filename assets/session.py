import json
SESSION_FILE="session.json"
class Sessions:
    @staticmethod
    def _load():
        try:
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    @staticmethod
    def _save(sessions):
        with open(SESSION_FILE, 'w') as f:
            json.dump(sessions, f, indent=4)

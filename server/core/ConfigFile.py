import yaml
import os
import time
import hashlib

class ConfigFile:
    
    def __init__(self, path):
        self.path = path
        self.last_modified = 0
        self.last_hash = ""
        try:
            with open(path, "r") as f:
                content = f.read()
                self.config = yaml.safe_load(content)
                
                if self.config is None:
                    print(f"Warning: Config file {path} is empty or invalid YAML. Using empty config.")
                    self.config = {}
                
                self.last_modified = os.path.getmtime(path)
                self.last_hash = self._calculate_hash(content)
            print(f"Config file {path} loaded successfully.")
        except FileNotFoundError:
            print(f"Config file {path} not found.")
            self.config = {}
            self.last_modified = 0
            self.last_hash = ""
        except yaml.YAMLError as e:
            print(f"Error parsing YAML config file {path}: {e}")
            self.config = {}
            self.last_modified = 0
            self.last_hash = ""

    #  this is for checking if the config file has changed (since if the hash is different it means the file has changed)
    def _calculate_hash(self, content):
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _has_changed(self):
        try:
            current_modified = os.path.getmtime(self.path)
            if current_modified > self.last_modified:
                with open(self.path, "r") as f:
                    content = f.read()
                    current_hash = self._calculate_hash(content)
                    if current_hash != self.last_hash:
                        return True, content
            return False, None
        except FileNotFoundError:
            return False, None

    # validating config file required fields 
    def validate(self):
        if not isinstance(self.config, dict):
            return False, "Config must be a dictionary"

        if "programs" not in self.config:
            return False, "Config must contain 'programs' section"

        if not isinstance(self.config["programs"], dict):
            return False, "'programs' must be a dictionary"

        # Validate each program configuration
        for program_name, program_config in self.config["programs"].items():
            if not isinstance(program_config, dict):
                return False, f"Program '{program_name}' configuration must be a dictionary"

            # Check required fields
            if "cmd" not in program_config:
                return False, f"Program '{program_name}' must have 'cmd' field"

            # Validate field types
            if "numprocs" in program_config and not isinstance(program_config["numprocs"], int):
                return False, f"Program '{program_name}' 'numprocs' must be an integer"

            if "autostart" in program_config and not isinstance(program_config["autostart"], bool):
                return False, f"Program '{program_name}' 'autostart' must be a boolean"

            if "autorestart" in program_config and program_config["autorestart"] not in ["always", "never", "unexpected", None]:
                return False, f"Program '{program_name}' 'autorestart' must be 'always', 'never', or 'unexpected'"

            if "exitcodes" in program_config and not isinstance(program_config["exitcodes"], list):
                return False, f"Program '{program_name}' 'exitcodes' must be a list"

            if "startretries" in program_config and not isinstance(program_config["startretries"], int):
                return False, f"Program '{program_name}' 'startretries' must be an integer"

            if "starttime" in program_config and not isinstance(program_config["starttime"], (int, float)):
                return False, f"Program '{program_name}' 'starttime' must be a number"

            if "stoptime" in program_config and not isinstance(program_config["stoptime"], (int, float)):
                return False, f"Program '{program_name}' 'stoptime' must be a number"

            if "stopsignal" in program_config and program_config["stopsignal"] not in ["HUP", "INT", "QUIT", "TERM", "KILL", "USR1", "USR2"]:
                return False, f"Program '{program_name}' 'stopsignal' must be one of: HUP, INT, QUIT, TERM, KILL, USR1, USR2"

            if "env" in program_config and not isinstance(program_config["env"], dict):
                return False, f"Program '{program_name}' 'env' must be a dictionary"

            if "umask" in program_config and not isinstance(program_config["umask"], int):
                return False, f"Program '{program_name}' 'umask' must be an integer"

        return True, "Config is valid"

    def reload(self):
        has_changed, content = self._has_changed()
        if has_changed:
            try:
                old_config = self.config.copy()
                self.config = yaml.safe_load(content)
                
                if self.config is None:
                    print(f"Warning: Config file {self.path} is empty or invalid YAML during reload. Using empty config.")
                    self.config = {}
                
                self.last_modified = os.path.getmtime(self.path)
                self.last_hash = self._calculate_hash(content)
                
                is_valid, message = self.validate()
                if not is_valid:
                    self.config = old_config  # Restore old config
                    return False, f"Invalid config: {message}"
                
                print(f"Config file {self.path} reloaded successfully.")
                return True, "Config reloaded successfully"
            except yaml.YAMLError as e:
                print(f"Error parsing YAML config file {self.path} during reload: {e}")
                return False, f"YAML parsing error: {e}"
            except Exception as e:
                print(f"Error reloading config file {self.path}: {e}")
                return False, f"Error reloading config: {e}"
        return False, "No changes detected"

    def check_for_changes(self):
        return self.reload()

    def __str__(self):
        return str(self.config)
        
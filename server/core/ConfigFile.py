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

    def validate(self):

        if not isinstance(self.config, dict):
            return False, "Config must be a dictionary"
        
        if "programs" not in self.config:
            return False, "Config must contain 'programs' section"
        
        if not isinstance(self.config["programs"], dict):
            return False, "'programs' must be a dictionary"
        
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
        
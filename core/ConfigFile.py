import yaml

class ConfigFile:
    
    def __init__(self, path):
        self.path = path
        try:
            with open(path, "r") as f:
                content = f.read()
                self.config = yaml.safe_load(content)
            print(f"Config file {path} loaded successfully.")
        except FileNotFoundError:
            print(f"Config file {path} not found.")
            self.config = {}
    
    def getConfig(self):
        return self.config

    def validate(self):
        pass

    #  
    def reload(self):
        pass

    def __str__(self):
        return self.config
        
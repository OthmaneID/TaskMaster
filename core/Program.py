import subprocess
import shlex


class Program:
    def __init__(self, name : str, ProgramConfig : dict):
        self.name = name
        self.cmd = ProgramConfig.get("cmd")
        self.process = None
        self.stdout = ProgramConfig.get("stdout")
        self.stderr = ProgramConfig.get("stderr")

        # verify if stdout and stderr files exist if not create them
        try:
            if self.stdout is not None:
                with open(self.stdout, "w") as f:
                    f.write("")
            if self.stderr is not None:
                with open(self.stderr, "w") as f:
                    f.write("")
        except Exception as e:
            print(f"Error creating stdout and stderr files for program {self.name}")
            exit(1)

        self.autostart = ProgramConfig.get("autostart", True)
        self.autorestart = ProgramConfig.get("autorestart")

        # for future use
        self.Memory = 0
        self.cpu = 0
        
        self.status = ""

    def run(self) -> None:

        self.process = subprocess.Popen(shlex.split(self.cmd), stdout=open(self.stdout, "w"), stderr=open(self.stderr, "w"))
        
        if self.process.poll() is None:
            self.status = "running"
        else:
            self.status = "down"
    

    def check_status(self):
        if self.process is not None:
            if self.process.poll() is None:
                self.status = "running"
            else:
                self.status = "down"
        else:
            self.status = "down"

    def getPid(self) -> int:
        if self.process.poll() is not None:
            return self.process.pid
        return -1
    
    def getStatus(self) -> str:
        return self.status


    def getName(self) -> str:
        return self.name
    
    def getProcess(self) -> subprocess.Popen:
        return self.process

    def kill(self) -> None:
        if self.process is not None :
            self.process.kill()
            self.process.wait()
            self.status = "down"
    
    def __str__(self) -> str:
        return f"Program {self.name} : status {self.status} , Memory {self.Memory} , CPU {self.cpu}"
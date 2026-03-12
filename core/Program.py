import subprocess
import shlex
import time
import os
import signal
from utils.child import handle_signal

class Program:
    # self.status can be 
    def __init__(self, name : str, ProgramConfig : dict):
        self.name = name
        self.cmd = ProgramConfig.get("cmd")
        self.process = None
        stdout = ProgramConfig.get("stdout", f"{self.name}.out") 
        stderr = ProgramConfig.get("stderr", f"{self.name}.err")
        self.env = ProgramConfig.get("env", {})

        self.workdir = ProgramConfig.get("workdir", ".")


        # handling umask
        current_umask = os.umask(0)
        os.umask(current_umask) # reset to original umask
        self.umask = ProgramConfig.get("umask", current_umask)
        print(f"Current umask for program {self.name} is {oct(self.umask)}")


        # verify if stdout and stderr files exist if not create them
        try:
            self.stdout = open(stdout, "w")
            self.stderr = open(stderr, "w")
        except Exception as e:
            print(f"Error creating stdout and stderr files for program {self.name}: {e}")
            exit(1)

        self.autostart = ProgramConfig.get("autostart", True)
        self.autorestart = ProgramConfig.get("autorestart")
        self.startretries = ProgramConfig.get("startretries", 0)
        self.starttime = ProgramConfig.get("starttime", 0)
        self.exitcodes = ProgramConfig.get("exitcodes", [0])
        self.stopsignal = ProgramConfig.get("stopsignal", "TERM")

        # for future use
        self.Memory = 0
        self.cpu = 0

        self.start_ts = 0
        
        self.status = "" # can be exited, backoff, fatal, starting, successful, down

    def run(self) -> None:

        self.process = subprocess.Popen(
                            shlex.split(self.cmd),
                            stdout=self.stdout, 
                            stderr=self.stderr, 
                            env=self.env, 
                            cwd=self.workdir,
                            umask=self.umask,
                            preexec_fn=lambda: handle_signal()
                                    # handle the signals in the child process 
                        )
        if self.process.poll() is None:
            self.status = "starting"
            self.start_ts = time.time()
        else:
            self.status = "down"


    def updateStatus(self):
        if self.process is not None:
            if self.process.poll() is None:
                # print(f"{self.name} : updatestatus")
                if self.start_ts + self.starttime > time.time():
                    self.status = "starting"
                else:
                    self.status = "successful"
            else: 
                if self.process.returncode in self.exitcodes:
                    self.status = "exited"
                else:
                    if self.start_ts + self.starttime > time.time():
                        self.status = "backoff"
                    else:
                        self.status = "fatal"


    # def kill(self) -> None:
    #     if self.process.poll() is None:
    #         self.process.kill()
    #         self.process.wait()
    #         # self.status = "exited"
    

    def __str__(self) -> str:
        return f"Program {self.name} : status {self.status} , Memory {self.Memory} , CPU {self.cpu}"
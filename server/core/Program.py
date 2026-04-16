import subprocess
import shlex
import time
import os
import signal

class Program:
    # self.status can be 
    def __init__(self, name : str, ProgramConfig : dict, processNum: int):
        self.name = name
        self.cmd = ProgramConfig.get("cmd")
        self.process = None
        stdout = ProgramConfig.get("stdout", f"{self.name}.out") 
        stderr = ProgramConfig.get("stderr", f"{self.name}.err")
        self.env = ProgramConfig.get("env", {})
        self.totalProcs = ProgramConfig.get("numprocs", 1)

        self.workdir = ProgramConfig.get("workdir", ".")


        # handling umask
        current_umask = os.umask(0)
        os.umask(current_umask) # reset to original umask
        self.umask = ProgramConfig.get("umask", current_umask)


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
        self.stoptime = ProgramConfig.get("stoptime", 1)
        self.exitcodes = ProgramConfig.get("exitcodes", [0])

        self.processNum = processNum
        SIGNALS = {
            "HUP": signal.SIGHUP,
            "INT": signal.SIGINT,
            "QUIT": signal.SIGQUIT,
            "TERM": signal.SIGTERM,
            "KILL": signal.SIGKILL,
            "USR1": signal.SIGUSR1,
            "USR2": signal.SIGUSR2,
        }
        self.stopsignal = SIGNALS.get(ProgramConfig.get("stopsignal", "TERM"), None)
        if self.stopsignal is None:
            print(f"Config Error: {ProgramConfig.get("stopsignal")} cannot be handeled, please use one of these : {list(SIGNALS.keys())}")
            exit(1)

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
                            preexec_fn=lambda: os.umask(self.umask),
                        )
        # self.process.
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
    

    def __str__(self) -> str:
        return f"Program {self.name}({self.processNum}) : status {self.status} , Memory {self.Memory} , CPU {self.cpu}"
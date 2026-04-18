import logging
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
        self.stdout_path = stdout
        self.stderr_path = stderr
        self.stdout = None
        self.stderr = None
        try:
            self.stdout = open(stdout, "a")
            self.stderr = open(stderr, "a")
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
        self.SIGNALS = {
            "HUP": signal.SIGHUP,
            "INT": signal.SIGINT,
            "QUIT": signal.SIGQUIT,
            "TERM": signal.SIGTERM,
            "KILL": signal.SIGKILL,
            "USR1": signal.SIGUSR1,
            "USR2": signal.SIGUSR2,
        }
        self.stopsignal = ProgramConfig.get("stopsignal", "TERM")
        if self.stopsignal not in ["HUP", "INT", "QUIT", "TERM", "KILL", "USR1", "USR2"]:
            print(f"Config Error: {ProgramConfig.get("stopsignal")} cannot be handeled, please use one of these : HUP, INT, QUIT, TERM, KILL, USR1, USR2")
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
            # print(f"Started {self.name}({self.processNum})")
            logging.info(f"Started {self.name}({self.processNum})")
        else:
            self.status = "down"
            print(f"Failed to start {self.name}({self.processNum})")
            logging.error(f"Failed to start {self.name}({self.processNum})")

    def stop(self):
        if self.process is not None and self.process.poll() is None:
            try:
                sig = self.SIGNALS[self.stopsignal]
                self.process.send_signal(sig)
                logging.info(f"Sent {self.stopsignal} signal to {self.name}({self.processNum})")
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=self.stoptime)
                    self.status = "stopped"
                    logging.info(f"{self.name}({self.processNum}) stopped gracefully")
                    return True
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.process.kill()
                    self.process.wait()
                    self.status = "stopped"
                    logging.warning(f"{self.name}({self.processNum}) killed after stoptime")
                    return True
            except Exception as e:
                logging.error(f"Error stopping {self.name}({self.processNum}): {e}")
                return False
        return False

    def restart(self):
        if self.process is not None and self.process.poll() is None:
            self.stop()
            self.run()
            return 1
        else:
            return 0

    def is_alive(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    def updateStatus(self):
        if self.process is not None:
            if self.is_alive():
                # Process is running
                if self.start_ts + self.starttime > time.time():
                    self.status = "starting"
                else:
                    self.status = "successful"
            else:
                # Process has exited
                if self.process.returncode in self.exitcodes:
                    self.status = "exited"
                else:
                    if self.start_ts + self.starttime > time.time():
                        self.status = "backoff"
                    else:
                        self.status = "fatal"
        else:
            # No process exists
            self.status = "down"


    def cleanup(self):
        if self.stdout and not self.stdout.closed:
            self.stdout.close()
        if self.stderr and not self.stderr.closed:
            self.stderr.close()

    def get_pid(self) -> int:
        if self.process and self.process.poll() is None:
            return self.process.pid
        return None

    def __str__(self) -> str:
        return f"Program {self.name}({self.processNum}) : status {self.status} , Memory {self.Memory} , CPU {self.cpu}"
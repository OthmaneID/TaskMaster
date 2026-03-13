import time
from core.Program import Program
from core.ConfigFile import ConfigFile
import logging



class Supervisor:

    def __init__(self, config : ConfigFile):
        try:
            self.config : ConfigFile = config
            self.programs : list[Program] = []
            
            # get the global configurations
            self.logfile = self.config.config.get("globals", dict()).get("logfile", "/tmp/taskmaster.log")
            logging.basicConfig(filename=self.logfile, filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s : %(message)s')

            # get Programs to supervise
            configObject = self.config.config
            if "programs" not in configObject.keys():
                raise Exception("Config parsing error: no 'programs' found")

            for program in configObject["programs"].keys():
                numprocs = configObject["programs"].get(program, {}).get("numprocs")
                # this is for handling multiple processes for each program
                for i in range(numprocs):
                    prog = Program(program, configObject["programs"][program], i+1)
                    self.programs.append(prog)
        except Exception as e:
            print(f"config file parsing error : {e}")


    # checks to program status , restarts programs that needs restarting , change status and other variables accordingly
    def monitor(self) -> None:
        # check status of all self.programs
        for program in self.programs:
            program.updateStatus()
            status = program.status
            print(f"{program.name}({program.processNum}) status: {status}, code: {program.process.returncode if program.process is not None else "None"}")
            # only restart if autorestart is true and retries is not 0
            if program.autorestart:
                if status in ["backoff", "fatal", "down"]:
                    if program.startretries > 0:
                            print(f"Restarting {program.name}({program.processNum}) in backoff, retries left: {program.startretries}")
                            program.startretries -= 1
                            program.run()
                            logging.info(f"Restarted {program.name}({program.processNum})")
                    else:
                        print(f"{program.name}({program.processNum}) : Max retries reached")
                        logging.info(f"{program.name}({program.processNum}) : Max retries reached")
        # we should add a logging system into a file provided in the conf.yaml or a default one instead
        # ...


    def run(self) -> None:

        for program in self.programs:
            if program.autostart:
                program.run()
                print(f"Started {program.name}({program.processNum})")
                logging.info(f"Started {program.name}({program.processNum})")

        # this is the main loop that monitors the programs 
        try:

            while True:
                self.monitor()
                print("\r")
                time.sleep(1)
        except KeyboardInterrupt as e:
            print(f"program interrupted : {e}")
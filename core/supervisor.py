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
            configObject = self.config.getConfig()
            if "programs" not in configObject.keys():
                raise Exception("Config parsing error: no 'programs' found")

            for program in configObject["programs"].keys():
                prog = Program(program, configObject["programs"][program])
                self.programs.append(prog)
        except Exception as e:
            print(f"config file parsing error : {e}")
            
    def getPrograms(self) -> list[dict[str, Program]]:
        return self.programs


    # checks to program status , restarts programs that needs restarting , change status and other variables accordingly
    def monitor(self) -> None:
        # check status of all self.programs
        for program in self.programs:
            program.updateStatus()
            status = program.status
            print(f"{program.name} status: {status}, code: {program.process.returncode if program.process is not None else "None"}")
            # only restart if autorestart is true and retries is not 0
            if program.autorestart:
                if status in ["backoff", "fatal", "down"]:
                    if program.startretries > 0:
                            print(f"Restarting {program.name} in backoff, retries left: {program.startretries}")
                            program.startretries -= 1
                            program.run()
                            print(f"Restarting {program.name}")
                            logging.info(f"Restarted {program.name}")
                    else:
                        logging.error(f"Max retries reached")
        # we should add a logging system into a file provided in the conf.yaml or a default one instead
        # ...


    def run(self) -> None:

        for program in self.programs:
            if program.autostart:
                program.run()
                print(f"Started {program.name}")
                logging.info(f"Started {program.name}")

        # this is the main loop that monitors the programs 
        while True:
            self.monitor()
            print("\r")
            time.sleep(1)

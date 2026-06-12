import json
import os
import time
import signal
from core.Program import Program
from core.ConfigFile import ConfigFile

import logging
from logging.handlers import SMTPHandler

from core.TcpServer import TcpServer
from core.handleRequest import HandleRequest
from dotenv import load_dotenv

load_dotenv()


class Supervisor:

    def __init__(self, config : ConfigFile):
        try:
            self.tcpServer = TcpServer()
            self.config : ConfigFile = config
            self.programs : list[Program] = []
            self.last_config_check = 0
            self.config_check_interval = 3  # Check every 3 seconds

            # get the global configurations
            self.logfile = self.config.config.get("globals", dict()).get("logfile", "/tmp/taskmaster.log")
            logging.basicConfig(filename=self.logfile, filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s : %(message)s')
            # mail handler for logging critical errors to email
            
            mailHandler = SMTPHandler(
                mailhost=("smtp.gmail.com", 587), 
                fromaddr=os.getenv("EMAIL"), 
                toaddrs=[os.getenv("EMAIL")], 
                subject="TaskMaster Alert", 
                credentials=(os.getenv("EMAIL"), os.getenv("GOOGLE_APP_PASSWORD")),
                secure=()
                )
            
            mailHandler.setLevel(logging.ERROR)
            mailHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s : %(message)s'))
            print("mailHandler created : ", mailHandler)
            logging.getLogger().addHandler(mailHandler)
            
            
            
            # get Programs to supervise
            self._load_programs()

            #  handle sighub to make it reload all program in case of config changes
            signal.signal(signal.SIGHUP, self._sighup_handler)


            # we need to add a feature to view how much resources are being used by each program and the total used resources (cpu power and ram)
        except Exception as e:
            print(f"config file parsing error : {e}")
            exit(1)

    def _handle_config(self):
        changed, message = self.config.check_for_changes()
        if changed:
            return self._handle_config_change(self.config.config, message)
        else:
            print(message)
            logging.info(message)
            return message

    def _sighup_handler(self, signum, frame):
        print("Received SIGHUP signal, reloading configuration...")
        logging.info("Received SIGHUP signal, reloading configuration...")
        self._handle_config()

    def _load_programs(self):

        configObject = self.config.config
        if "programs" not in configObject.keys():
            raise Exception("Config parsing error: no 'programs' found")

        new_programs = []
        for program_name in configObject["programs"].keys():
            program_config = configObject["programs"][program_name]
            numprocs = program_config.get("numprocs", 1)
            # this is for handling multiple processes for each program
            for i in range(numprocs):
                prog = Program(program_name, program_config, i+1)
                new_programs.append(prog)
        
        # Stop old programs that are no longer in config
        self._stop_removed_programs(new_programs)
        self.programs = new_programs

    def _stop_removed_programs(self, new_programs: list[Program]):
        """Stop programs that are no longer in the config"""
        new_program_names = set()
        for prog in new_programs:
            new_program_names.add(f"{prog.name}_{prog.processNum}")

        for old_prog in self.programs:
            old_prog_key = f"{old_prog.name}_{old_prog.processNum}"
            if old_prog_key not in new_program_names:
                if old_prog.process and old_prog.process.poll() is None:
                    print(f"Stopping removed program {old_prog.name}({old_prog.processNum})")
                    old_prog.process.terminate()
                    logging.info(f"Stopped removed program {old_prog.name}({old_prog.processNum})")

    def _handle_config_change(self, new_config, message):
        print(f"Config change detected: {message}")
        logging.info(f"Config change detected: {message}")
        
        try:
            # Reload logging configuration if it changed
            new_logfile = new_config.get("globals", dict()).get("logfile", "/tmp/taskmaster.log")
            if new_logfile != self.logfile:
                self.logfile = new_logfile
                logging.shutdown()
                logging.basicConfig(filename=self.logfile, filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s : %(message)s')
                print(f"Log file changed to: {self.logfile}")
                logging.info(f"Log file changed to: {self.logfile}")
            
            # save old programs and create new program objects to compare which ones are new and what programs have been modified 
            old_programs = self.programs.copy()
            self._load_programs()
            
            # Start new programs and restart modified ones
            self._apply_program_changes(old_programs)
            return "Configuration reloaded successfully"
            
        except Exception as e:
            print(f"Error applying config changes: {e}")
            logging.error(f"Error applying config changes: {e}")
            return "Error applying config changes: {e}"


    def _apply_program_changes(self, old_programs: list[Program]):
        """Apply changes to programs based on new config"""
        old_programs_dict = {}
        for prog in old_programs:
            key = f"{prog.name}_{prog.processNum}"
            old_programs_dict[key] = prog
        
        new_programs_dict = {}
        for prog in self.programs:
            key = f"{prog.name}_{prog.processNum}"
            new_programs_dict[key] = prog
        
        # Start new programs
        for key, new_prog in new_programs_dict.items():
            if key not in old_programs_dict:
                if new_prog.autostart:
                    new_prog.run()
                    # print(f"Started new program {new_prog.name}({new_prog.processNum})")
                    logging.info(f"Started new program {new_prog.name}({new_prog.processNum})")

        for key, new_prog in new_programs_dict.items():
            # if the program is old, check if it's config has changed
            if key in old_programs_dict:
                old_prog = old_programs_dict[key]

                if self._program_config_changed(old_prog, new_prog):
                    #  if changed , stop old program if running and start new one if autostart is true
                    if old_prog.process and old_prog.process.poll() is None:
                        print(f"Restarting modified program {new_prog.name}({new_prog.processNum})")
                        old_prog.process.terminate()
                        logging.info(f"Stopped modified program {new_prog.name}({new_prog.processNum})")
                    
                    if new_prog.autostart:
                        new_prog.run()
                        print(f"Started modified program {new_prog.name}({new_prog.processNum})")
                        logging.info(f"Started modified program {new_prog.name}({new_prog.processNum})")


    def _program_config_changed(self, old_prog: Program, new_prog: Program):
        old_config = {
            'cmd': old_prog.cmd,
            'env': old_prog.env,
            'numprocs': old_prog.totalProcs,
            'workdir': old_prog.workdir,
            'umask': old_prog.umask,
            'autostart': old_prog.autostart,
            'autorestart': old_prog.autorestart,
            'startretries': old_prog.startretries,
            'starttime': old_prog.starttime,
            'stoptime': old_prog.stoptime,
            'exitcodes': old_prog.exitcodes,
            'stopsignal': old_prog.stopsignal
        }
        
        new_config = {
            'cmd': new_prog.cmd,
            'env': new_prog.env,
            'numprocs': new_prog.totalProcs,
            'workdir': new_prog.workdir,
            'umask': new_prog.umask,
            'autostart': new_prog.autostart,
            'autorestart': new_prog.autorestart,
            'startretries': new_prog.startretries,
            'starttime': new_prog.starttime,
            'stoptime': new_prog.stoptime,
            'exitcodes': new_prog.exitcodes,
            'stopsignal': new_prog.stopsignal
        }
        
        return old_config != new_config


    def monitor(self) -> None:
        
        
        programs_copy = self.programs.copy()
        
        for program in programs_copy:
            program.updateStatus()
            status = program.status
            # check if the program has autorestart always or unexpected, and if unexpected check for exitcodes
            if program.autorestart == "always" or (program.autorestart == "unexpected" and program.process and program.process.returncode not in program.exitcodes):
                if status in ["backoff", "fatal", "down"]:
                    if program.startretries > 0:
                            # print(f"Restarting {program.name}({program.processNum}) in backoff, retries left: {program.startretries}")
                            program.startretries -= 1
                            program.run()
                            logging.info(f"Restarted {program.name}({program.processNum})")
                    else:
                        # print(f"{program.name}({program.processNum}) : Max retries reached")
                        logging.info(f"{program.name}({program.processNum}) : Max retries reached")

    def handle_remote_command(self, cmd:list[str]):
        handler = HandleRequest()
        if cmd[0] == "list":
            return handler.Program_list(self.programs)
        if cmd[0] == "status":
            return handler.status(cmd[1], programs=self.programs)

        if cmd[0] == "start":
            if len(cmd) > 2:
                return handler.start(cmd[1], process_num=int(cmd[2]), programs=self.programs)
            return handler.start(cmd[1], programs=self.programs)

        if cmd[0] == "stop":
            if len(cmd) > 2:
                return handler.stop(cmd[1], process_num=int(cmd[2]), programs=self.programs)
            return handler.stop(cmd[1], programs=self.programs) # thinking about adding another argument which is the process number ()

        if cmd[0] == "restart":
            if len(cmd) > 2:
                return handler.restart(cmd[1], process_num=int(cmd[2]), programs=self.programs)
            return handler.restart(cmd[1], programs=self.programs)

        if cmd[0] == "RamUsage":
            ram_usage = []
            for program in self.programs:
                ram_usage.append({
                    "name" : program.name,
                    "proces" : program.processNum,
                    "ram_usage" : program.get_ram_usage()
                })
                # ram_usage[f"{program.name} ({program.processNum})"] = program.get_ram_usage()
            return json.dumps(ram_usage)
        
        if cmd[0] == "config_reload":
            return json.dumps({"data": self._handle_config()})

        return json.dumps([{"error": "Unknown command"}])


    def run(self) -> None:
        programs_copy = self.programs.copy()
        
        for program in programs_copy:
            if program.autostart:
                program.run()

        # this is the main loop that monitors the programs and checks config
        try:
            while True:
                client_socket, data = self.tcpServer.check_for_new_connection()
                if client_socket and data:
                    response = self.handle_remote_command(data.split(" "))
                    self.tcpServer.send_response(client_socket, response)
                self.monitor()
                print("\r")
                time.sleep(1)
        except KeyboardInterrupt as e:  
            print(f"program interrupted : {e}")
            # Cleanup: stop all programs
            for program in self.programs:
                if program.process and program.process.poll() is None:
                    program.process.terminate()
                    # print(f"Stopped {program.name}({program.processNum})")
                    logging.info(f"Stopped {program.name}({program.processNum})")
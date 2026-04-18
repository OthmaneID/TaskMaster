import json
import time
import signal
from core.Program import Program
from core.ConfigFile import ConfigFile
import logging

from core.TcpServer import TcpServer
from core.handleRequest import HandleRequest



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

            # get Programs to supervise
            self._load_programs()

            #  handle sighub to make it reload all program in case of config changes
            signal.signal(signal.SIGHUP, self._sighup_handler)
        except Exception as e:
            print(f"config file parsing error : {e}")
            exit(1)

    def _sighup_handler(self, signum, frame):
        print("Received SIGHUP signal, reloading configuration...")
        logging.info("Received SIGHUP signal, reloading configuration...")
        changed, message = self.config.check_for_changes()
        if changed:
            self._handle_config_change(self.config.config, message)
        else:
            print("No configuration changes detected")
            logging.info("No configuration changes detected")

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

    def _stop_removed_programs(self, new_programs):
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
            
            # Reload programs
            old_programs = self.programs.copy()
            self._load_programs()
            
            # Start new programs and restart modified ones
            self._apply_program_changes(old_programs)
            
        except Exception as e:
            print(f"Error applying config changes: {e}")
            logging.error(f"Error applying config changes: {e}")

    def _apply_program_changes(self, old_programs):
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
        
        # Handle modified programs (restart if config changed)
        for key, new_prog in new_programs_dict.items():
            if key in old_programs_dict:
                old_prog = old_programs_dict[key]

                if self._program_config_changed(old_prog, new_prog):
                    if old_prog.process and old_prog.process.poll() is None:
                        print(f"Restarting modified program {new_prog.name}({new_prog.processNum})")
                        old_prog.process.terminate()
                        logging.info(f"Stopped modified program {new_prog.name}({new_prog.processNum})")
                    
                    if new_prog.autostart:
                        new_prog.run()
                        print(f"Started modified program {new_prog.name}({new_prog.processNum})")
                        logging.info(f"Started modified program {new_prog.name}({new_prog.processNum})")


    def _program_config_changed(self, old_prog, new_prog):
        """Check if program configuration has changed"""
        # Compare key configuration parameters
        old_config = {
            'cmd': old_prog.cmd,
            'env': old_prog.env,
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
        current_time = time.time()
        if current_time - self.last_config_check >= self.config_check_interval:
            changed, message = self.config.check_for_changes()
            if changed:
                self._handle_config_change(self.config.config, message)
            self.last_config_check = current_time
        
        programs_copy = self.programs.copy()
        
        for program in programs_copy:
            program.updateStatus()
            status = program.status
            # print(f"{program.name}({program.processNum}) status: {status}, code: {program.process.returncode if program.process is not None else "None"}")
            if program.autorestart:
                if status in ["backoff", "fatal", "down"]:
                    if program.startretries > 0:
                            # print(f"Restarting {program.name}({program.processNum}) in backoff, retries left: {program.startretries}")
                            program.startretries -= 1
                            program.run()
                            logging.info(f"Restarted {program.name}({program.processNum})")
                    else:
                        # print(f"{program.name}({program.processNum}) : Max retries reached")
                        logging.info(f"{program.name}({program.processNum}) : Max retries reached")


    #  we need to handle each command (list, status <service_name>, stop <service_name>, restart <service_name>, start <service_name>)
    def handle_remote_command(self, cmd:list[str]):
        handler = HandleRequest()
        if cmd[0] == "list":
            return handler.Program_list(self.programs)

        if cmd[0] == "status":
            return handler.status(cmd[1], self.programs)

        if cmd[0] == "start":
            return handler.start(cmd[1], self.programs)

        if cmd[0] == "stop":
            return handler.stop(cmd[1], self.programs)

        if cmd[0] == "restart":
            return handler.restart(cmd[1], self.programs)

        return json.dumps({"error": "Unknown command"})


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
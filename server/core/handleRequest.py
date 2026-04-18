
import json
from core.Program import Program 


class HandleRequest:
    def __init__(self):
        pass

    def Program_list(self, programs: list[Program]):
        res = {"data" : [{"name": program.name, "status": program.status} for program in programs]}
        return json.dumps(res, indent=4)

    def start(self, arg:str, programs: list[Program]):
        name = arg
        started_processes = 0
        found_program = False
        for program in programs:
            if program.name == name:
                # exited, backoff, fatal, starting, successful, down 
                if program.status in ["exited", "fatal", "down"]:
                    program.run()
                    if program.status == "starting":
                        started_processes += 1
                found_program = True

        if not found_program:
            return json.dumps({"error": "Program not found"})
        if started_processes == 0:
            return json.dumps({"error": "Program is already running or trying to start"})
        return json.dumps({"data": f"Started {started_processes} processes of \"{name}\""})

    def stop(self, service_name:str, programs: list[Program]):
        stopped_processes = 0
        found_program = False
        for program in programs:
            if program.name == service_name:
                if program.status in ["starting", "successful"]:
                    program.stop()
                    if program.status == "stopped":
                        stopped_processes += 1
                found_program = True

        if not found_program:
            return json.dumps({"error": "Program not found"})
        if stopped_processes == 0:
            return json.dumps({"error": "Program is not running or already stopped"})
        return json.dumps({"data": f"Stopped {stopped_processes} processes of \"{service_name}\""})

    def restart(self, service_name:str, programs: list[Program]):
        restarted_processes = 0
        found_program = False
        for program in programs:
            if program.name == service_name:
                program.restart()
                if program.status == "starting":
                    restarted_processes += 1
                found_program = True

        if not found_program:
            return json.dumps({"error": "Program not found"})
        if restarted_processes == 0:
            return json.dumps({"error": "Failed to restart program"})
        return json.dumps({"data": f"Restarted {restarted_processes} processes of \"{service_name}\""})

    def status(self, arg:str, programs: list[Program]):
        for program in programs:
                if program.name == arg:
                    # info to return name, number of processes, status, stop signal, exit codes
                    return json.dumps({"data": {
                        "name": program.name,
                        "procs": program.totalProcs,
                        "status": program.status,
                        "stop_signal": program.stopsignal,
                        "exit_codes": program.exitcodes
                    }})
        return json.dumps({"error": "Program not found"})
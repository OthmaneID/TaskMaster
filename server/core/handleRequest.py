


import json
from server.core.Program import Program


class HandleRequest:
    def __init__(self):
        pass

    def list(self, programs: list[Program]):
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

    def stop(self, arg:str, programs: list[Program]):
        pass

    def restart(self, arg:str, programs: list[Program]):
        pass

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
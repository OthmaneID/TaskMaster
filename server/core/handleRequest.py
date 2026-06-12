
import json
from multiprocessing import process
from core.Program import Program 


class HandleRequest:
    def __init__(self):
        pass

    def Program_list(self, programs: list[Program]):
        res = {"data" : [{"name": program.name, "process_num":program.processNum, "status": program.status} for program in programs]}
        return json.dumps(res, indent=4)

    def start(self, service_name:str, process_num: int = 0, programs: list[Program] = None):
        name = service_name
        started_processes = 0
        found_program = False
        for program in programs:
            if program.name == name:
                if process_num > 0 and program.processNum != process_num:
                    continue
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
        return json.dumps({"data": f"Started {started_processes} processe(s) of \"{name}\""})

    def stop(self, service_name:str, process_num: int = 0, programs: list[Program] = None):
        stopped_processes = 0
        found_program = False
        for program in programs:
            if program.name == service_name:
                if process_num > 0 and program.processNum != process_num:
                    continue
                if program.status in ["starting", "successful"]:
                    program.stop()
                    if program.status == "stopped":
                        stopped_processes += 1
                found_program = True

        if not found_program:
            return json.dumps({"error": "Program not found"})
        if stopped_processes == 0:
            return json.dumps({"error": "Program is not running or already stopped"})
        return json.dumps({"data": f"Stopped {stopped_processes} processe(s) of \"{service_name}\""})

    def restart(self, service_name:str, process_num: int = 0, programs: list[Program] = None):
        restarted_processes = 0
        found_program = False
        for program in programs:
            if program.name == service_name:
                if process_num > 0 and program.processNum != process_num:
                    continue
                program.restart()
                if program.status == "starting":
                    restarted_processes += 1
                found_program = True

        if not found_program:
            return json.dumps({"error": "Program not found"})
        if restarted_processes == 0:
            return json.dumps({"error": "Failed to restart program"})
        return json.dumps({"data": f"Restarted {restarted_processes} processes of \"{service_name}\""})

    def status(self, service_name:str, programs: list[Program]):
        processes = []
        stopsignal = ""
        exitcodes = []
        for program in programs:
                if program.name == service_name:
                    stopsignal = program.stopsignal
                    exitcodes = program.exitcodes
                    # info to return name, number of processes, status, stop signal, exit codes7
                    processes.append({
                        "status" : program.status,
                        "process_num": program.processNum,
                        "retries": program.startretries
                    })
        if len(processes) == 0:
            return json.dumps({"error": "Program not found"})
        return json.dumps({"data": {
            "name": service_name,
            "procs": processes,
            "stop_signal": stopsignal,
            "exit_codes": exitcodes
        }})
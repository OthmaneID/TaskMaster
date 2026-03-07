import yaml
import shlex

import subprocess
#  steps

# 1. basic read of the configfile
# 2. parse the configfile to get the process information
# 3. run the process


def parseConfigFile(configFileObg: object, programs: list):

    with open("conf.yaml", "r") as f:
        configFileObg = yaml.safe_load(f)
    for key, program in configFileObg.get("programs").items():
        print(key, program)
        programs.append(
            {
                "name":key,
                "command":program.get("cmd")
            }
        )
    # programs.extend(configFileObg.get("programs"))
    



def runProcess(programs: list, processes: list):
    for program in programs:
        process = subprocess.Popen(shlex.split(program["command"]))
        processes.append(process)
        print(f"Process {program['name']} started with PID {process.pid}")
    
    

def waitForProcesses(processes: list):
    for process in processes:
        print(f"Waiting for process {process.pid} to finish")
        process.wait()
        print(f"Process {process.pid} finished")

# def 

if __name__ == "__main__":
    try:
        configFileObg = None 
        programs = []
        processes = []
        parseConfigFile(configFileObg, programs)
        runProcess(programs, processes)
        waitForProcesses(processes)
    except KeyboardInterrupt:
        print("User interrupted")
    except Exception as e:
        print(f"Error: {e}")




    # print(configFileObg)
    # print(programs)
    # print("this is just a small program practice running a simple supervisor program for a single process")


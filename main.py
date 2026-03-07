from core.ConfigFile import ConfigFile
from core.supervisor import Supervisor

from core.Program import Program



if __name__ == "__main__":
    config = ConfigFile("conf.yaml")
    supervisor = Supervisor(config)

    programs = supervisor.getPrograms()

    for program in programs:
        if program["program"].autostart:
            program["program"].run()
            print(f"Started {program['name']}")



    for program in programs:
        if program["program"].getStatus() == "running":
            try:

                print(f"wating for program {program['name']}")
                program["program"].getProcess().wait()
                print(f"Program {program['name']} finished")
            except Exception as e:
                print(f"Error waiting for program {program['name']}: {e}")
                program["program"].kill()
                print(f"Program {program['name']} killed")

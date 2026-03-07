from core.Program import Program
from core.ConfigFile import ConfigFile




class Supervisor:

    def __init__(self, config : ConfigFile):
        try:
            self.config : ConfigFile = config
            self.programs : list[dict[str, Program]] = []
            self.globals = self.config.get("globals")

            # get Programs to supervise
            configObject = self.config.getConfig()
            if "programs" not in configObject.keys():
                raise Exception("Config parsing error: no 'programs' found")

            for program in configObject["programs"].keys():
                prog = Program(program, configObject["programs"][program])
                self.programs.append(
                    {
                        "name": program,
                        "program": prog
                    }
                )
        except Exception as e:
            print(f"config file parsing error : {e}")
            
    def getPrograms(self) -> list[dict[str, Program]]:
        return self.programs


import os

from core.ConfigFile import ConfigFile
from core.supervisor import Supervisor
import sys


if __name__ == "__main__":
    print("Starting TaskMaster... PID :", os.getpid())
    config_path = sys.argv[1] if len(sys.argv) > 1 else "conf.yaml"
    config = ConfigFile(config_path)
    supervisor = Supervisor(config)

    supervisor.run()
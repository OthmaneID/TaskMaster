from cmd import Cmd
import json
from TcpClient import TcpClient

class MyShell(Cmd):
    prompt = "taskmaster> "
    intro = "Welcome to TaskMaster. Type help or ? to list commands."

    def default(self, line: str) -> None:
        print(f"Unknown command: {line}")


    #  what should happen if the service is already running?
    def do_start(self, service_name: str, process_num: int=0, *useless_args):
        """
        *****************Help*****************
        ------Start a service
        ------Usage: start <service_name> <process number (optional)\n
        """
        response = self._send_to_server(f"start {service_name} {process_num}")
        res : dict = json.loads(response)
        
        if res.get("error"):
            print(res["error"])
        else:
            print(res["data"])
        return False
        # return True

    #  need to clarify if the stop ignores the config params like autorestart, startretries etc.
    def do_stop(self, service_name: str, process_num: int=0, *useless_args):
        """
        *****************Help*****************
        ------Stop a service
        ------Usage: stop <service_name> <process number (optional)>\n
        """
        response = self._send_to_server(f"stop {service_name} {process_num}")
        res : dict = json.loads(response)
        
        if res.get("error"):
            print(res["error"])
        else:
            print(res["data"])
        return False
    

    # clarify if the retry is going to consume the retry count or ignore the config params
    def do_restart(self, service_name: str, process_num: int=0, *useless_args):
        """
        *****************Help*****************
        ------Restart a service
        ------Usage: restart <service_name> <process number (optional)>\n
        """
        response = self._send_to_server(f"restart {service_name} {process_num}")
        res : dict = json.loads(response)
        
        if res.get("error"):
            print(res["error"])
        else:
            print(res["data"])
        return False
        # return True

    def do_status(self, service_name: str, *useless_args):
        """
        *****************Help*****************
        ------Get the status of a service
        ------Usage: status <service_name>\n
        """
        response = self._send_to_server(f"status {service_name}")
        res : dict = json.loads(response)

        if res.get("data"):
            data : dict = res['data']
            print(f"\n{'='*50}")
            print(f"Program Status: {data.get('name', 'N/A')}")
            print(f"{'='*50}")
            print(f"  Name        : {data.get('name', 'N/A')}")
            print(f"  Stop Signal : {data.get('stop_signal', 'N/A')}")
            print(f"  Exit Codes  : {data.get('exit_codes', 'N/A')}")
            
            procs = data.get('procs', [])
            if procs:
                print(f"\n  Processes ({len(procs)}):")
                for proc in procs:
                    print(f"    - Process #{proc.get('process_num', 'N/A')}")
                    print(f"      Status  : {proc.get('status', 'N/A')}")
                    print(f"      Retries : {proc.get('retries', 'N/A')}")
            
            print(f"{'='*50}\n")
        else:
            if res.get('error'):
                print(f"Error: {res['error']}")
            else:
                print(f"No data available")
        return False
        # return True

    
    def do_list(self,arg, *useless_args):
        """
        *****************Help*****************
        ------List all services that are on config file
        ------Usage: list\n
        """
        print("waiting for response ...")
        response = self._send_to_server("list")
        res = json.loads(response)
        for prog in res["data"]:
            print(f" - {prog['name']}  #({prog["process_num"]}) :  {prog['status']}")
        # handle reponse accordingly
        # ...
        return False
        # return True

    def do_config_reload(self, arg, *useless_args):
        """
        *****************Help*****************
        ------Reload the existing configuration file
        ------Usage: config_reload\n
        """
        print("Reloading configuration...")
        response = self._send_to_server("config_reload")
        res = json.loads(response)
        if res.get("data"):
            print(res["data"])
        else:
            print("Failed to reload configuration")
        return False


    # def _do_wait_for_response()


    def _send_to_server(self, message):
        client = TcpClient()
        client.send(message)
        # client.socket.settimeout(1)
        response = client.receive()
        if not response:
            print("TimeOut waiting for response")
        # client.socket.close()
        return response  


    def do_exit(self, arg):
        """
        *****************Help*****************
        ------Exit the shell
        """
        print("Exiting...")
        return True


    def _do_EOF(self, arg):
        print("\nEOF received!")
        return True

    def emptyline(self):
        pass


from cmd import Cmd
import json
from TcpClient import TcpClient

class MyShell(Cmd):
    prompt = "taskmaster> "
    intro = "Welcome to TaskMaster. Type help or ? to list commands."

    def default(self, line: str) -> None:
        print(f"Unknown command: {line}")


    #  what should happen if the service is already running?
    def do_start(self, arg):
        """
        *****************Help*****************
        ------Start a service
        ------Usage: start <service_name>\n
        """
        response = self._send_to_server(f"start {arg}")
        res : dict = json.loads(response)
        
        if res.get("error"):
            print(res["error"])
        else:
            print(res["data"])
        return False
        # return True

    # clarify if the retry is going to consume the retry count or ignore the config params
    def do_restart(self, arg):
        """
        *****************Help*****************
        ------Restart a service
        ------Usage: restart <service_name>\n
        """
        response = self._send_to_server(f"restart {arg}")
        res : dict = json.loads(response)
        
        if res.get("error"):
            print(res["error"])
        else:
            print(res["data"])
        return False
        # return True

    def do_status(self, arg):
        """
        *****************Help*****************
        ------Get the status of a service
        ------Usage: status <service_name>\n
        """
        response = self._send_to_server(f"status {arg}")
        res : dict = json.loads(response)

        if res.get("data"):
            data : dict = res['data']
            print(f"\n{'='*50}")
            print(f"Program Status: {data.get('name', 'N/A')}")
            print(f"{'='*50}")
            print(f"  Name        : {data.get('name', 'N/A')}")
            print(f"  Processes   : {data.get('procs', 'N/A')}")
            print(f"  Status      : {data.get('status', 'N/A')}")
            print(f"  Stop Signal : {data.get('stop_signal', 'N/A')}")
            print(f"  Exit Codes  : {data.get('exit_codes', 'N/A')}")
            print(f"{'='*50}\n")
        else:
            if res.get('error'):
                print(f"Error: {res['error']}")
            else:
                print(f"No data available")
        return False
        # return True

    
    def do_list(self, arg):
        """
        *****************Help*****************
        ------List all services that are on config file
        ------Usage: list\n
        """
        print("waiting for response ...")
        response = self._send_to_server("list")
        res = json.loads(response)
        for prog in res["data"]:
            print(f" - {prog['name']} :  {prog['status']}")
        # handle reponse accordingly
        # ...
        return False
        # return True


    #  need to clarify if the stop ignores the config params like autorestart, startretries etc.
    def do_stop(self, arg):
        """
        *****************Help*****************
        ------Stop a service
        ------Usage: stop <service_name>\n
        """
        response = self._send_to_server(f"stop {arg}")
        res : dict = json.loads(response)
        
        if res.get("error"):
            print(res["error"])
        else:
            print(res["data"])
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


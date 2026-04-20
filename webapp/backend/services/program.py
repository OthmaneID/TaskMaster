import json
from utils.TcpClient import TcpClient


def listPrograms():
    client = TcpClient()
    client.send("list")
    response = client.receive()
    return json.loads(response)

def statusProgram(service_name: str):
    client = TcpClient()
    client.send(f"status {service_name}")
    response = client.receive()
    return json.loads(response)

def startProgram(service_name: str, process_num: int = None):
    client = TcpClient()
    if process_num is not None:
        client.send(f"start {service_name} {process_num}")
    else:
        client.send(f"start {service_name}")
    response = client.receive()
    return json.loads(response)

def stopProgram(service_name: str, process_num: int = None):
    client = TcpClient()
    if process_num is not None:
        client.send(f"stop {service_name} {process_num}")
    else:
        client.send(f"stop {service_name}")
    response = client.receive()
    return json.loads(response)


def restartProgram(service_name: str, process_num: int = None):
    client = TcpClient()
    if process_num is not None:
        client.send(f"restart {service_name} {process_num}")
    else:
        client.send(f"restart {service_name}")
    response = client.receive()
    return json.loads(response)


def getRamUsage():
    client = TcpClient()
    client.send("RamUsage")
    response = client.receive()
    return json.loads(response)

import signal
from MyShell import MyShell


def sigint_handle(signum, frame):
    print("\nInterrupt received!")
    exit(0)

if __name__ == "__main__":
    client = MyShell()
    signal.signal(signal.SIGINT, sigint_handle)

    client.cmdloop()
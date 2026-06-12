import sys

if __name__ == "__main__":
    # run server
    sys.subprocess.Popen([sys.executable, "python3", "server/main.py"])
    if len(sys.argv) > 1 and sys.argv[1] == "client":
        # run client
        sys.subprocess.Popen([sys.executable, "python3", "client/main.py"])
    elif len(sys.argv) > 1 and sys.argv[1] == "web":
        # run web interface
        sys.subprocess.Popen([sys.executable, "npm", "run", "dev"])
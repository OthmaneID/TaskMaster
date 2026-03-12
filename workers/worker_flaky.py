import random
print("Worker Flaky: Random exit")
code = random.choice([0, 1])
print(f"Exiting with code {code}")
exit(code)

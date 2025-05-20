from circus import get_arbiter

myprogram = {"cmd":"sudo python3 run_experiments.py", "numprocesses": 1}

arbiter = get_arbiter([myprogram])
try:
    arbiter.start()
finally:
    arbiter.stop()


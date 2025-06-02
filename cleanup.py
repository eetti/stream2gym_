import os

os.system("sudo mn -c ")
os.system("sudo ps aux | grep 'bandwidth-monitor' | grep python | awk '{print $2}' | sudo xargs kill -9")
os.system("sudo ps aux | grep 'run_experiments' | grep python | awk '{print $2}' | sudo xargs kill -9")
<<<<<<< HEAD
os.system("sudo ps aux | grep '/users/grad/etti/pinet' | grep python | awk '{print $2}' | sudo xargs kill -9")
os.system("sudo ps aux | grep 'use-cases/disconnection' | grep python | awk '{print $2}' | sudo xargs kill -9")

=======
os.system("sudo ps aux | grep '/home/etti/pinet' | grep python | awk '{print $2}' | sudo xargs kill -9")
>>>>>>> 5e9f00e9ba6e5622ae34017c140a19515999ff01

#!/usr/bin/python3
import os

import string    
import random  

for i in range(1000):
    with open("use-cases/varying-networking-conditions/varying-link-latency/word-count/MFSTDataDir/"+str(i+1)+".txt", "w") as out:
        S = 1024  # number of characters in the string.  
        # call random.choices() string module to find the string in Uppercase + numeric data.  
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))    
        # print("The randomly generated string is : " + str(ran))
        out.write(str(ran))



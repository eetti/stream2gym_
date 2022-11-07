#!/bin/usr/python3

import matplotlib.pyplot as plt

fig = plt.figure()

# nConcurrentUsers = [20, 40, 60,80,100]
# avgExecTimeRound1 = [4740, 4112, 4636.0, 3868.0, 4996.0]
# avgExecTimeRound2 = [3374, 4084, 4859.0, 3146.923076923 , 5493]
# avgExecTimeRound3 = [6075, 3434, 4168, 4027.8 , 3326]

# plt.plot(nConcurrentUsers,avgExecTimeRound1,color='blue',linestyle='dashed', label='Round1')
# plt.plot(nConcurrentUsers,avgExecTimeRound2,color='red',linestyle='dashed', label='Round2')
# plt.plot(nConcurrentUsers,avgExecTimeRound3,color='green',linestyle='dashed', label='Round3')

nConcurrentUsers = [1, 20, 40, 60,80,100]
avgExecTimeRound1 = [47.996, 1342.71, 2077.465, 2359.824, 2592.634, 2540.529]
plt.plot(nConcurrentUsers,avgExecTimeRound1,color='blue',linestyle='dotted')


plt.xlabel('Concurrent users', fontsize=16)
plt.ylabel('Average execution time(ms)', fontsize=16)
plt.title('Distributed streaming processing execution time',fontsize=20)
plt.legend()
plt.show()


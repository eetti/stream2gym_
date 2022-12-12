# example command: sudo python3 use-cases/app-testing/millitary-coordination/scripts/measurePeakCPU-Mem.py --log-dir use-cases/app-testing/millitary-coordination/logs/cpu-mem --host-list 2,4,6,8,10
#!/bin/usr/python3

import argparse
import matplotlib.pyplot as plt

# taking log-directory and comma separated list of hosts
parser = argparse.ArgumentParser(description='Script for visualizing peak CPU and peak memory utilisation.')
parser.add_argument('--log-dir', dest='logDir', type=str, help='Log directory of cpu and memory usage')
parser.add_argument('--host-list', dest='hostStr', type=str, help='Comma separated list of hostnodes')

args = parser.parse_args()
logDir = args.logDir
hostStr = args.hostStr
hostList = hostStr.split(',')

peakCPUUsage = []
peakMemUsage = []
for index, item in enumerate(hostList):
    # measure Peak CPU usage for all hosts
    with open(logDir+'/'+item+'-hosts-5min-run-cpu.log') as cpuFP:
        cpuLst = [float(x) for x in cpuFP.read().split()]
        peakCPUUsage.append(max(cpuLst))

    # measure Peak Memory usage for all hosts
    with open(logDir+'/'+item+'-hosts-5min-run-mem.log') as memFP:
        memLst = [float(x) for x in memFP.read().split()]
        peakMemUsage.append(max(memLst))

# print(peakMemUsage)
peakMemPercentage = []
for item in peakMemUsage:
    memPercentage = round((float(item)/15953.4)* 100.0, 2)
    peakMemPercentage.append(memPercentage)
# print(peakMemPercentage)


print('Host list: '+str(hostList))
print('Peak CPU usage(%): '+str(peakCPUUsage))
print('Peak Memory usage(%): '+str(peakMemPercentage))

# plot and save peak CPU usage with respect to hosts
plt.plot(hostList,peakCPUUsage,color='blue')
plt.xlabel('Number of hosts', fontsize=16)
plt.ylabel('Peak CPU usage(%)', fontsize=16)
minCPU = int(min(peakCPUUsage))
maxCPU = int(max(peakCPUUsage))
plt.yticks(range(minCPU,maxCPU+10, 5))
plt.savefig(logDir+"/CPUUsage.png",format='png', bbox_inches="tight")

# clearing the existing plot
plt.cla()
plt.clf()

# plot and save peak memory usage with respect to hosts
plt.plot(hostList,peakMemPercentage,color='red')
plt.xlabel('Number of hosts', fontsize=16)
plt.ylabel('Peak Memory usage(%)', fontsize=16)
minMem = int(min(peakMemPercentage))
maxMem = int(max(peakMemPercentage))
plt.yticks(range(minMem, maxMem+10, 5))
plt.savefig(logDir+"/MemoryUsage.png",format='png', bbox_inches="tight")


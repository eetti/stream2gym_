# example command: sudo python3 use-cases/app-testing/millitary-coordination/scripts/measurePeakCPU-Mem.py --log-dir use-cases/app-testing/millitary-coordination/logs/cpu-mem/round1 --host-list 2,4,6,8,10
#!/bin/usr/python3

import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import statistics

def clearExistingPlot():
    # clear the previous figure
    plt.close()
    plt.cla()
    plt.clf() 

def plotUtilizationCDF(utilz, logDir, counter, hostList, plotChoice='CPU'):
    colorLst = ['r','g','b', 'y','k']
    hist_kwargs = {"linewidth": 2,
                  "edgecolor" :'salmon',
                  "alpha": 0.4, 
                  "color":  "w",
                #   "label": "Histogram",
                  "cumulative": True}
    kde_kwargs = {'linewidth': 3,
                  'color': colorLst[counter],
                  "alpha": 0.7,
                #   'label':'Kernel Density Estimation Plot',
                  'cumulative': True}

    sns.distplot(utilz, hist_kws=hist_kwargs, kde_kws=kde_kwargs).set(xlim=(0,100))
    plt.legend(labels=hostList,  title = "nHosts")
    
    # Add labels
    plt.title('CDF of '+plotChoice+' utilization')
    plt.xlabel(plotChoice+' utilization(%)')
    plt.ylabel('CDF')
    
    plt.savefig(logDir+"/"+plotChoice+"CDF.png",format='png', bbox_inches="tight")

print(sns.__version__)
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
medianCPUUsage = []
for index, item in enumerate(hostList):
    # measure Peak CPU usage for all hosts
    with open(logDir+'/'+item+'-hosts-5min-run-cpu.log') as cpuFP:
        cpuLst = [float(x) for x in cpuFP.read().split()]
        # print('CPU usage for '+item+' hostnodes: ')
        # print(cpuLst)

        plotUtilizationCDF(cpuLst, logDir, index, hostList, 'CPU')
        peakCPUUsage.append(max(cpuLst))
        # Median of list
        medCpu = statistics.median(cpuLst)
        medianCPUUsage.append(medCpu)

    # measure Peak Memory usage for all hosts
    with open(logDir+'/'+item+'-hosts-5min-run-mem.log') as memFP:
        memLst = [float(x) for x in memFP.read().split()]
        # plotUtilizationCDF(memLst, logDir, index, hostList, 'Memory')
        peakMemUsage.append(max(memLst))
clearExistingPlot()
print(peakMemUsage)
peakMemPercentage = []
for item in peakMemUsage:
    memPercentage = round((float(item)/15953.4)* 100.0, 2)
    peakMemPercentage.append(memPercentage)
# print(peakMemPercentage)


print('Host list: '+str(hostList))
print('Peak CPU usage(%): '+str(peakCPUUsage))
print('Median CPU usage(%): '+str(medianCPUUsage))
print('Peak Memory usage(%): '+str(peakMemPercentage))

# # clearing the existing plot
clearExistingPlot()

# plot and save median CPU usage with respect to hosts
plt.plot(hostList,medianCPUUsage,color='blue')
plt.xlabel('Number of hosts', fontsize=16)
plt.ylabel('Median CPU usage(%)', fontsize=16)
# minMedCPU = int(min(medianCPUUsage))
# maxMedCPU = int(max(medianCPUUsage))
# plt.yticks(range(minMedCPU,maxMedCPU+10, 5))
plt.savefig(logDir+"/medianCPUUsage.png",format='png', bbox_inches="tight")

# # plot and save peak CPU usage with respect to hosts
# plt.plot(hostList,peakCPUUsage,color='blue')
# plt.xlabel('Number of hosts', fontsize=16)
# plt.ylabel('Peak CPU usage(%)', fontsize=16)
# minPeakCPU = int(min(peakCPUUsage))
# maxPeakCPU = int(max(peakCPUUsage))
# plt.yticks(range(minPeakCPU,maxPeakCPU+10, 5))
# plt.savefig(logDir+"/peakCPUUsage.png",format='png', bbox_inches="tight")

# clearing the existing plot
clearExistingPlot()

# plot and save peak memory usage with respect to hosts
plt.plot(hostList,peakMemPercentage,color='red')
plt.xlabel('Number of hosts', fontsize=16)
plt.ylabel('Peak Memory usage(%)', fontsize=16)
minMem = int(min(peakMemPercentage))
maxMem = int(max(peakMemPercentage))
plt.yticks(range(minMem, maxMem+10, 5))
plt.savefig(logDir+"/MemoryUsage.png",format='png', bbox_inches="tight")


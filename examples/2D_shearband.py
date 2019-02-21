import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from granular_speckles import shearband
from scipy.ndimage.filters import gaussian_filter as conv_gaussian
import sys

# Import the file with the matrix of correlation time, with dimensions (columns, rows, samples)
matrices = np.load("data_shearband/dati/allCorrTimeMap_MinLoc_Sp10_NOCUTOFF.npy")
# Set the array of velocities in respect to samples of previous matrix.
vel = np.array([0.05, 0.07, 0.1, 0.3, 0.5, 0.7, 1.2, 1.5])

# set which samples to use by command line argument, otherwise hardcoded
if len(sys.argv) > 1:
    print(sys.argv[1])
    data = [int(x) for x in list(sys.argv[1].split(','))]
else:
    data = [1, 2, 3, 4, 6, 7]
print("Plot samples:{}".format(data))

speeds = vel[data]
matrices = np.mean(matrices[data],axis=2)
matrices = matrices.T / np.max(matrices, axis=1)
matrices = matrices.T

# smooth the data with gaussian convolution
matrices = np.array([conv_gaussian(matrix, 0.2, 0)
          for matrix in matrices])

# get jump_values distribution for each matrix
jumps_values = shearband(speeds, matrices, plot=True)
print(jumps_values)

# matrices = np.array([average_matrices[h, :]
#                      for h in range(len(speeds))])

fig0, ax1 = plt.subplots()
ax1.pcolor(matrices.T)
c = "r"
# plt.scatter([ x + 0.5 for x in range(len(data))], , c="r")
ax1.scatter([x + 0.5 for x in range(len(data))], jumps_values[0, :], color=c)
ax1.scatter([x + 0.5 for x in range(len(data))], jumps_values[0, :] + jumps_values[1, :] * 0.5, color=c, marker=".")
ax1.scatter([x + 0.5 for x in range(len(data))], jumps_values[0, :] - jumps_values[1, :] * 0.5, color=c, marker=".")
fig0.savefig("CorrelationMap.pdf", ext="pdf", dpi=300)

times = ([], [], [])
last_band = int(jumps_values[0, -1] + jumps_values[1, -1] * 0.5)
first_band = int(jumps_values[0, 0] - jumps_values[1, 0] * 0.5)
for enum in range(len(data)):
    # last_band= int(jumps_values[0,enum]-jumps_values[1,enum]*0.5)
    # first_band= int(jumps_values[0,enum]+jumps_values[1,enum]*0.5)
    # last_band= int(jumps_values[0,enum]+jumps_values[1,enum]*0.5)
    # first_band= int(jumps_values[0,enum]-jumps_values[1,enum]*0.5)
    # start_space= int(jumps_values[0,enum]+jumps_values[1,enum]*0.5)
    times[0].append(np.mean(matrices[enum, :first_band]))
    times[1].append(np.mean(matrices[enum, last_band:first_band]))
    print(last_band, first_band, matrices[enum, :])
    times[2].append(np.mean(matrices[enum, last_band:]))
print(times)

def linear(x, m, b):
    return m * x + b

color = ["b", "r", "g"]
fig, ax2 = plt.subplots()
LABEL = ["solid", "shear band", "fluid"]
for index in range(len(times)):
    ax2.plot(speeds, times[index], c=color[index], marker="o", label=LABEL[index])
    popt, pvar = curve_fit(linear, speeds, times[index])
    # ax2.plot(speeds,[x*popt[0]+popt[1] for x in speeds],c=color[index])
ax2.semilogx()
# ax2.semilogy()
ax2.legend()

# fig.savefig("CorrelationTime.pdf", ext="pdf", dpi=300)
plt.show()

# clean_matrices = [list(mobilmean(mobmean,x)) for x in average_matrices]

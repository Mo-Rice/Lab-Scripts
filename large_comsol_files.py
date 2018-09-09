import Scattering_analysis as sa
import pandas as pd
import numpy as np
from sys import argv

# This is intended for comsol files with multiple eigen frequecies, the format of which
# is as follows:
# r, z, z displacement, frequency, total strain, z displacement 2, frequency 2, total strain 2,....

script, inputfile, output1, output2 = argv

# Files
if1 = inputfile + ".txt"
fn1 = output1 + ".txt"
fn2 = output2 + ".txt"

s_tot = 0 #  running sum of scattered light
f = open(fn1, 'w')
f_1 = open(fn2, 'w')
f_1.write('Mode frequency [Hz],Scattered Light [W],Sum [W]\n')
f.write("#radius [m], mode amplitude[1/m] \n")

print('Importing data from ' + if1 + '.')
d = pd.read_csv(if1, sep ='\s+', skiprows=9, header=None)
col = len(d.columns)
r = d[0]
z = d[1]
m = 2 # for tracking position in column space

while m < col:
	w = d[m]
	m+=1
	f_m = d[m][0] 
	m+=1
	E = d[m][0] 
	m+=1

	print('Determining mode shape for ' + str(f_m) + ' Hz.')
	print("-" * 30)

	f.write("F: " + str(f_m) + " Hz" + "\n")
	f.write("E: " + str(E) + " J" + "\n")

	r_i, v_n = sa.mode_shape(r, z, w, E)

	for i in range(len(r_i)):
		f.write(str(r_i[i]) + "," + str(v_n[i]) + "\n")

	print('Integrating...')
	s = sa.integrate2(v_n, r_i)
	s_tot = s_tot + s

	print("Light power scattered by mode: " + str(s) + " W.")
	f_1.write(str(f_m) + "," + str(s) + "," + str(s_tot) + "\n")
	f.write("-" * 30 + "\n")

print("-" * 30)
print("Total light scattered: " + str(s_tot))
f.close()
f_1.close()
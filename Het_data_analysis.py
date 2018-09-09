import time, logging, math, sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.fftpack import fft
plt.rcParams.update({'font.size': 22})

PD_gain = 1.44e3 # V/W
h = 6.626e-34 # Planck's constant
nu = 281954887218045.06 # 1064nm laser frequency

def ss_fft(x, s_f):
	"produces an fft of a given array and sampling frequency"

	N = len(x)
	T = 1/s_f
	yf = fft(x)
	xf = np.linspace(0.0, 1.0/(2*T), N//2)
	plt.plot(xf, 2.0/N*np.abs(yf[0:N//2]), 'k-')
	plt.xlabel('Frequency [Hz]')
	plt.ylabel('Amplitude [V]')
	plt.grid(True)
	plt.show()

def import_moku_file(file):
	"""Imports content from moku to three arrays containing the 
	time stamps and data from channels 1 and 2"""

	data = pd.read_csv(file, sep=',', skiprows=8)
	t = data['% Time']
	ch1 = data[' Output (V)']
	ch2 = data[' Auxiliary output (V)']

	return t, ch1, ch2

def import_net_file(file):
	data = pd.read_csv(file)
	s = data['Sample']
	ch1 = data['Ch1']
	ch2 = data['Ch2']

	return s, ch1, ch2

def z_n(x, s, demod_freq, sampling_frequency):
	"""Using sample number rather than the time stamps
	   to generate the second demod"""

	z_n = []
	sum_I = 0
	sum_Q = 0
	N = int(len(x))

	for i, j in zip(x, s):
		I = i*np.sin(2.0*np.pi*j*demod_freq/sampling_frequency) 
		Q = i*np.cos(2.0*np.pi*j*demod_freq/sampling_frequency)  	
		sum_I += I
		sum_Q += Q
		z = ((sum_I**2) + (sum_Q**2)) / N
		z_n.append(z)

	z_1 = np.array(z_n)

	return z_1

def z_n_t(x, t, demod_freq):
	"""This function can be used to generate Z(f) 
	given an I or Q and the secondary demod freq"""

	N = int(len(x))
	z_n = []
	sum_I = 0
	sum_Q = 0
	counter = 1

	for i,j in zip(x, t):
		I = i*np.sin(2.0*np.pi*j*demod_freq) 
		Q = i*np.cos(2.0*np.pi*j*demod_freq) 
		sum_I += I
		sum_Q += Q
		z = ((sum_I**2) + (sum_Q**2))/(N**2)
		z_n.append(z)

	z_1 = np.array(z_n)

	return z_1

def p_s(z_n, laser_power):
	"Converts an array containing Z(N) data in photons per second"
	
	p_s = 4*z_n/((PD_gain**2)*h*nu*laser_power)

	return p_s

def plot(x, y, x_label, y_label, title):
	fig, ax = plt.subplots()
	plt.loglog(x, y)
	plt.xlabel(x_label)
	plt.ylabel(y_label)
	plt.title(title)
	ax.grid(True, which = 'both')
	plt.show()
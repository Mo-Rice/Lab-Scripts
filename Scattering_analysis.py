import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
import scipy.integrate

# When defining the Comsol files, we need to maintain data format
# Standard: Z Displacement(w) , frequency, Total elastic strain energy
# R and Z are the fist columns by default, for axisymetric models, this becomes
# more complicated for non-axisymmetric models.

rc = 2245
w_0 = 0.012030470340136271
z = 2160.4724697507813
lam = 1064e-9
z_r = np.pi*(w_0**2)/lam
w = w_0*np.sqrt(1+(z/z_r)**2)
guoy = np.arctan(z/z_r)
k = 2*np.pi/lam
j = np.complex(0,1)

# defunct done in other script.
def import_2D_comsol_file(filename):
	"Imports comsol file for axisymmetrical mirror modes"

	data = pd.read_csv(filename, skiprows=9, header=None, sep='\s+')
	r = data[0]
	z = data[1]
	w = data[2]
	E = data[4][0]

	return r, z, w, E

def mode_shape(r, z, w, E):
	"Acquires the mode shape for a given vector, then scales it to E in mode"

	n = []
	r_i = []
	d_i = []

	for i in range(len(z)):
		if z[i] == 0.2:
			n.append(i)

	for i in n:
		r_i.append(r[i])
		d_i.append(w[i])

	h_kt = 0.5 * 1.380648E-23 * 300 # 1.2*k*T for scaling the amplitude
	s = E/h_kt # Scaling total energy in each mode to 1/2*k*T
	a_s = np.sqrt(s) # This energy is proptional sqrt of E, model as a spring.
	v_n = d_i/a_s # scale displacement vector.

	return r_i, v_n

def mode_fit(r, v_n):
	"Fits the mode from comsol using polyfit"
	R2 = 0
	n = 0

	while R2 < 0.999999:
		f = np.polyfit(r, v_n, n)
		f1d = np.poly1d(f)
		v_fit = [f1d(i) for i in r]
		R2 = r2_score(v_n, v_fit)
		n+=1

	return n, v_fit, f1d, R2

# should implement the integration by hand for better understanding.
def integrate2(v_n, x_1):
	"Numerical integral without an interpolation function."

	u_0 = np.array([np.sqrt(2/np.pi)*np.exp(-j*guoy)*np.exp(-j*k*(r**2/2*rc)-(r**2/w**2)) for r in x_1])
	u_0_conj = np.array(np.conj(u_0))
	f_0 =  x_1*u_0*u_0_conj*(k*v_n)**2
	s = 4*np.pi*scipy.integrate.simps(f_0, x_1, x_1[1]-x_1[0])

	return np.real(s)

def integrate(f1d, a=0, b=0.17, N=10000):
	" Numerical integral using the interpolation function."

	r = np.linspace(a+(b-a)/(2*N), b-(b-a)/(2*N), N)
	v = np.array([f1d(i) for i in r])
	u = np.array([np.sqrt(2/np.pi)*np.exp(-j*guoy)*np.exp(-j*k*(i**2/2*rc)-(i**2/w**2)) for i in r])
	u_con = np.array(np.conj(u))
	ff = r*u[:, 0]*u_con[:,0]*(v*k)**2
	s = 4*np.pi*np.sum(ff)*(b-a)/N

	return s

# Mauricio Diaz-Ortiz Jr
# 12 July 2018

# scaling factor do a test to recheck gaines out of the moku.

from pymoku import Moku
from pymoku.instruments import LockInAmp
import time

# Call the Moku we wish to use and deploy the lock-in amplifier
m = Moku('10.244.25.31')
i = m.deploy_instrument(LockInAmp)
# f_test = 1e3+100

# Set up the lock-in such that I/Q are output after filtering, set high to bypass
# , and each data frame that is output contains the data from I/Q
# i.set_outputs('x', 'y')
i.set_outputs('x', 'sine')
i.set_lo_output(1.0, 1100, 0)	# this in the loop)

i.set_filter(3.5e6,1)
i.set_demodulation('internal', 1e3)
i.set_monitor('A', 'I')
i.set_monitor('B', 'Q')
i.set_trigger('A', 'rising', 0)

# Sampling rate correspond to filling the entire moku buffer of 16,384 samples and I assume they average every 16 samples
# The time base generated should correspond to the sampling rate when the frame is set to this length.
# This can be confirmed by calling i.get_samplerate().
print('At what rate would you like to log data to file?')
sampling_rate = float(input('> '))
timebase = 16384/sampling_rate 
#i.set_timebase(0, timebase) 
i.set_samplerate(sampling_rate)
i.commit()

print('Please enter a file name.')
filename = input('> ') + '.csv'
f = open(filename, 'w')
#f.write('Sample,Time,Ch1,Ch2\n')
f.write('Sample,Ch1,Ch2\n')

print('Amount of time to fill buffer: ' + str(timebase))
print('Buffer count')
buff_no = int(input('> '))
t_0 = buff_no*timebase+5

data = i.get_realtime_data()

# first_time = time.time()
final_time = time.time() + t_0
first_frame = 0
next_frame = 0

while time.time() <= final_time:
	data = i.get_realtime_data()
	ch1 = data.ch1
	ch2 = data.ch2
	#t_1 = data.time
	wid = data.waveformid
	# print('<', time.time()-first_time, '/', t_0, '>' ,end='\r')
	
	if first_frame == 0:
		first_frame = wid
		next_frame = first_frame + 1

		for n in range(len(ch1)):
			#f.write(str(n) + ',' + str(t_1[n]) + ',' + str(ch1[n])+ ',' + str(ch2[n]) + '\n')
			f.write(str(n) + ','  + str(ch1[n])+ ',' + str(ch2[n]) + '\n')

	elif wid == next_frame:

		for n in range(len(ch1)):
			#f.write(str(n + 1024*(next_frame - first_frame)) + ',' + 
			#		str(t_1[n] + timebase*(next_frame - first_frame)) + ',' 
			#		+ str(ch1[n])+ ',' + str(ch2[n]) + '\n')
			f.write(str(n + 1024*(next_frame - first_frame)) + ',' +  
					+ str(ch1[n])+ ',' + str(ch2[n]) + '\n')

		next_frame += 1
		
f.close()
m.close()


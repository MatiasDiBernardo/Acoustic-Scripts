import numpy as np


def number_of_modes(n_modes):
	"""
	Return a list of the diferent convinations of modes where
	n_modes defines the amount of convintations by (n_modes**3 - 1)
	"""
	nx_list = []
    
	for i in range(n_modes):
		for j in range(n_modes):
			for k in range(n_modes):
				nx_list.append([i,j,k])

	nx_list = np.array(nx_list)
    
	return nx_list[1:]

def modes(width_x,width_y, high_z, sound_speed=343,possible_convinations=6 ):
	"""
	Returns a dictionary with the resonance frequency and the mode

	width_x, width_y, high_z: Dimensions of the room in meters
	sound_speed: Default 343 in meters per second
	possible_convinations: Default in 6. Convinations of modes ** 3

	"""
	nx = number_of_modes(possible_convinations)
	modes = np.zeros(len(nx))
	dic_modes = {}

	for i in range(len(nx)):
		modes[i] = (sound_speed/2) * np.sqrt( (nx[i,0]/width_x)**2 + (nx[i,1]/width_y)**2 + (nx[i,2]/high_z)**2 )
		dic_modes.setdefault(modes[i], nx[i])

	return dic_modes

def show_result(modes_dic, number_to_show):
	"""
	Display in console the frequency and mode in order
	"""

	for i in sorted(modes_dic.keys())[:number_to_show]:
		print('Frequency: {:.3f}  -  Mode: {}'.format(i, modes_dic[i]))
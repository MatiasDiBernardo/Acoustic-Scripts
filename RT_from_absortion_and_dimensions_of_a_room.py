import numpy as np

def average_alpha(alpha, surface):
	"""
	Retun list with the average alpha according to the absortion conditions
	alpha: Numpy array with the values of absortion per material and frecuency 
	surface: Numpy array with the surface of an specific material in the room in m^2
	The index of the absortion and the surface must match
	"""
	if len(alpha.shape) == 1:
		alpha_prom = (sum(alpha * surface))/sum(surface)
	else:
		alpha_prom = np.zeros(len(alpha[0,:]))        
		for i in range(len(alpha[0,:])):
			alpha_prom[i] = (sum(alpha[:,i] * surface))/sum(surface)
	return alpha_prom


def RT_calculation(volume_room, absortion, suface, rt_type='sabine'):
	"""
	Return a list with the reverb time of the room
	volume_room: In m^3
	absortion: Numpy array with the values of absortion per material and frecuency 
	surface: Numpy array with the surface of an specific material in the room in m^2
	rt_type: Default is sabine. Optional 'norris', 'milington', 'eyring'

	"""
	
	average_absortion = average_alpha(absortion,surface)

	if rt_type == 'sabine':
		return (0.161 * volume_room) / (average_absortion * sum(surface))

	if rt_type == 'norris':
		return (0.161 * volume_room) /(-1 * np.log(1 - average_absortion) * sum(surface))

	if rt_type == 'millington':
		if len(absortion.shape) == 1:
			rt_milington =  (0.161* volume_room)/(-1 * sum(np.log(1 - absortion) * surface))
		else:
			rt_milington = np.zeros(len(absortion[0,:]))        
			for i in range(len(alpha[0,:])):
				rt_milington[i] = (0.161* volume_room)/(-1 * sum(np.log(1 - absortion[:,i]) * surface))
		return rt_milington

	if rt_type == 'eyring':
		if len(absortion.shape) == 1:
			rt_eyring =  (0.161* volume_room)/(-sum(surface) * np.log(1 - ( 1/sum(surface) * sum(absortion * surface))))
		else:
			rt_eyring = np.zeros(len(absortion[0,:]))        
			for i in range(len(alpha[0,:])):
				rt_eyring[i] = (0.161* volume_room)/(-sum(surface) * np.log(1 - ( 1/sum(surface) * sum(absortion[:,i] * surface))))
		return rt_eyring

def R_room(absortion, surface):
	average_absortion = average_alpha(absortion,surface)

	return (average_absortion * sum(surface))/(1 - average_absortion)

def show_rt(rt_calculation, freqs):
	print(f'Frequencies: ', freqs)
	print(f'RT: ', rt_calculation)

#Example

freq_of_absortion = [50,100,200,400]

alpha_wall = [0.07, 0.04, 0.03, 0.02]
alpha_celling = [0.01, 0.06, 0.08, 0.1]
alpha_floor = [0.76, 0.86, 0.56, 0.35]

sup_wall = 54
sup_celling = 20
sup_floor = 20

alpha = np.array([alpha_wall, alpha_celling, alpha_floor])
surface = np.array([sup_wall, sup_celling, sup_floor])


RT_sabine = RT_calculation(60, alpha, surface, rt_type='sabine')
RT_norris = RT_calculation(60, alpha, surface, rt_type='norris')
RT_milington = RT_calculation(60, alpha, surface, rt_type='millington')
RT_eyring = RT_calculation(60, alpha, surface, rt_type='eyring')

print('Sabine')
show_rt(RT_sabine, freq_of_absortion)
print('Norris')
show_rt(RT_norris, freq_of_absortion)
print('Millington')
show_rt(RT_milington, freq_of_absortion)
print('Eyring')
show_rt(RT_eyring, freq_of_absortion)

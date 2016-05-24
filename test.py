import time
import math
import random
from specs import *

# generate a random circuit
def generate_random_circuit(num_comp, ratio_sensor_comp):
	num_sensor = int(math.ceil(num_comp * ratio_sensor_comp))
	num_cont = 2 * num_comp - 2

	G = nx.DiGraph()
	'''
	generate the topology with number of components, sensors, and contactors
	'''

	return G

# generate random controllable contactor list
def generate_random_cc(G, ratio_cc):
	name_data = nx.get_edge_attributes(G, 'name').values()
	all_contactors = []
	for i in name_data:
		if all_contactors.count(i) == 0:
			all_contactors.append(i)
	num_cc = int(math.floor(float(len(all_contactors)) * ratio_cc))
	con_conts = random.sample(all_contactors, num_cc)
	return con_conts

# generate random dict with value 0 or 1
def generate_dict(a_list):
	a_dict = {}
	for i in a_list:
		a_dict[i] = random.randint(0, 1)
	return a_dict

# verify whether the results are the same
def verifier(a, b):
	if a != b:
		print 'Error: two results are not the same!'
		exit()
	return 0
import time
import math
import random
from specs import *

# generate a random circuit
# The circuit created has contraints including:
#   Only TRUs and sensors can have a wire connected to other components; others must have a contactor
#   Generators cannot connect with other generators with a contactor
#   Number of edges connected to generators or sensors or TRUs must be 1 or 2
#   Number of edges connected to buses can be any integer larger than 0
#   The inport of TRU must have a live path with the DC buses
#   The outport of TRU must have a live path with the AC buses
#   Generators are in the AC part
def generate_random_circuit(num_comp, ratio_sensor_comp):
	num_sensor = int(math.ceil(num_comp * ratio_sensor_comp))
	num_generator = random.randint(1, num_comp - 1)
	num_TRU = num_comp - num_generator
	num_bus = num_comp
	num_DC_bus = random.randint(1, num_bus - 1)
	num_AC_bus = num_bus - num_DC_bus
	DC_part = []
	AC_part = []
	generators = []

	G = nx.DiGraph()
	num = 1 # Set the initial number of nodes
	# Create nodes and assign AC and DC part
	for i in range(0, num_sensor):
		G.add_node(str(num), name = 'S' + str(i+1), type = 'sensor')
		if random.randint(0, 1) == 0:
			AC_part.append(str(num))
		else:
			DC_part.append(str(num))
		num = num + 1
	for i in range(0, num_generator):
		G.add_node(str(num), name = 'G' + str(i+1), type = 'generator')
		generators.append(str(num))
		num = num + 1
	for i in range(0, num_TRU):
		G.add_node(str(num), name = 'T' + str(i+1) + '_dc', type = 'rectifier_dc')
		G.add_node(str(num) + '_ac', name = 'T' + str(i+1) + '_ac', type = 'rectifier_ac')
		G.add_edge(str(num) + '_ac', str(num), type = 'wire')
		AC_part.append(str(num) + '_ac')
		DC_part.append(str(num))
		num = num + 1
	for i in range(0, num_DC_bus):
		G.add_node(str(num), name = 'B' + str(i+1), type = 'bus')
		DC_part.append(str(num))
		num = num + 1
	for i in range(num_DC_bus, num_AC_bus + num_DC_bus):
		G.add_node(str(num), name = 'B' + str(i+1), type = 'bus')
		AC_part.append(str(num))
		num = num + 1

	# Create edges between generators and AC components
	num_cont = 1
	for i in generators:
		num_neighbors = random.randint(1, 2)
		if num_neighbors == 2 and len(AC_part) == 1:
			num_neighbors = 1
		neighbors = random.sample(AC_part, num_neighbors)
		for j in neighbors:
			if G.node[j]['type'] == 'bus':
				G.add_edges_from([(i, j), (j, i)], name = 'C' + str(num_cont), type = 'contactor')
				num_cont = num_cont + 1
			else:
				edge_type = random.choice(['wire', 'contactor'])
				if edge_type == 'contactor':
					G.add_edges_from([(i, j), (j, i)], name = 'C' + str(num_cont), type = 'contactor')
					num_cont = num_cont + 1
				else:
					G.add_edges_from([(i, j), (j, i)], type = 'wire')
				if G.node[j]['type'] == 'rectifier_ac':
					AC_part.remove(j)
				else:
					if len(G.neighbors(j)) > 1:
						AC_part.remove(j)

	# Create other AC edges
	# len_AC = len(AC_part)
	# for k in range(0, len_AC - num_AC_bus):
	while len(AC_part) > num_AC_bus:
		i = AC_part[0]
		AC_part.remove(i)
		if G.node[i]['type'] == 'rectifier_ac':
			j = random.choice(AC_part)
			edge_type = random.choice(['wire', 'contactor'])
			if edge_type == 'contactor':
					G.add_edges_from([(i, j), (j, i)], name = 'C' + str(num_cont), type = 'contactor')
					num_cont = num_cont + 1
			else:
					G.add_edges_from([(i, j), (j, i)], type = 'wire')
			if G.node[j]['type'] == 'rectifier_ac':
				AC_part.remove(j)
			else:
				if len(G.neighbors(j)) > 1 and G.node[j]['type'] != 'bus':
					AC_part.remove(j)
		else:
			if G.node[i]['type'] == 'sensor':
				num_neighbors = random.randint(1, 2) - len(G.neighbors(i))
				if num_neighbors > 0:
					if num_neighbors == 2 and len(AC_part) == 1:
						num_neighbors = 1
					neighbors = random.sample(AC_part, num_neighbors)
					for j in neighbors:
						edge_type = random.choice(['wire', 'contactor'])
						if edge_type == 'contactor':
							G.add_edges_from([(i, j), (j, i)], name = 'C' + str(num_cont), type = 'contactor')
							num_cont = num_cont + 1
						else:
							G.add_edges_from([(i, j), (j, i)], type = 'wire')
						if G.node[j]['type'] == 'rectifier_ac':
							AC_part.remove(j)
						else:
							if len(G.neighbors(j)) > 1 and G.node[j]['type'] != 'bus':
								AC_part.remove(j)

	# Create edges between AC buses
	candidates = copy.copy(AC_part)
	for k in range(0, len(AC_part) - 1):
		i = candidates[0]
		candidates.remove(candidates[0])
		num_neighbors = random.randint(0, len(candidates))
		neighbors = random.sample(candidates, num_neighbors)
		for j in neighbors:
			G.add_edges_from([(i, j), (j, i)], name = 'C' + str(num_cont), type = 'contactor')
			num_cont = num_cont + 1

	# Create DC edges
	while len(DC_part) > num_DC_bus:
		i = DC_part[0]
		DC_part.remove(i)
		if G.node[i]['type'] == 'rectifier_dc':
			j = random.choice(DC_part)
			edge_type = random.choice(['wire', 'contactor'])
			if edge_type == 'contactor':
					G.add_edges_from([(i, j), (j, i)], name = 'C' + str(num_cont), type = 'contactor')
					num_cont = num_cont + 1
			else:
					G.add_edges_from([(i, j), (j, i)], type = 'wire')
			if G.node[j]['type'] == 'rectifier_dc':
				DC_part.remove(j)
			else:
				if len(G.neighbors(j)) > 1 and G.node[j]['type'] != 'bus':
					DC_part.remove(j)
		else:
			if G.node[i]['type'] == 'sensor':
				num_neighbors = random.randint(1, 2) - len(G.neighbors(i))
				if num_neighbors > 0:
					if num_neighbors == 2 and len(DC_part) == 1:
						num_neighbors = 1
					neighbors = random.sample(DC_part, num_neighbors)
					for j in neighbors:
						edge_type = random.choice(['wire', 'contactor'])
						if edge_type == 'contactor':
							G.add_edges_from([(i, j), (j, i)], name = 'C' + str(num_cont), type = 'contactor')
							num_cont = num_cont + 1
						else:
							G.add_edges_from([(i, j), (j, i)], type = 'wire')
						if G.node[j]['type'] == 'rectifier_dc':
							DC_part.remove(j)
						else:
							if len(G.neighbors(j)) > 1 and G.node[j]['type'] != 'bus':
								DC_part.remove(j)

	# Create edges between DC buses
	candidates = copy.copy(DC_part)
	for k in range(0, len(DC_part) - 1):
		i = candidates[0]
		candidates.remove(candidates[0])
		num_neighbors = random.randint(0, len(candidates))
		neighbors = random.sample(candidates, num_neighbors)
		for j in neighbors:
			G.add_edges_from([(i, j), (j, i)], name = 'C' + str(num_cont), type = 'contactor')
			num_cont = num_cont + 1

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

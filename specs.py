'''Copyright (c) 2014, The Regents of the University of Michigan
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
	list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
	this list of conditions and the following disclaimer in the documentation
	and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
	contributors may be used to endorse or promote products derived from
	this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
		 SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# This file includes multiple functions regarding both assertions and 
# guarantees of a circuit, the user instruction is commented before each function
'''

import networkx as nx
import subprocess
import csv
import ast

#read in a netlist file and create a corresponding
#network graph
def read_netlist(filename):
	f = open(filename,'r')
	content = f.read()
	f.close()
  
	G = nx.DiGraph()

	tups = content.split('\n')
	g_tups = []
	c_tups = []
	b_tups = []
	t_tups = []
	s_tups = []
	for i in range(0,len(tups)):
		line = tups[i]
		#skip empty line
		if line == '': continue
		#skip comment line
		elif line[0] == '#': continue
		#stop on reading .end
		elif line == '.end': break
		else:
			#declare nodes in directed graph
			x = line.split(' ')
			x_name = x[0]
			x_type = x[-1]
			x_num = x[-2]
			#if is bus
			if x_name[0]=='B':
				x_type = x[-2]
				x_num = x[-3]
				b_tups.append(line)
			elif x_name[0]=='C':
				c_tups.append(line)
			elif x_name[0]=='T':
				t_tups.append(line)
			elif x_name[0]=='G' or x_name[0]=='A':
				g_tups.append(line)
			elif x_name[0]=='S':
				s_tups.append(line)
			#create nodes
			if x_type != 'contactor' and x_type != 'TRU':
				G.add_node(x_num,name=x_name,type=x_type)
			elif x_type == 'TRU':
				G.add_node(x_num,name=x_name+'_dc',type='rectifier_dc')
				G.add_node(x_num+'_ac',name=x_name+'_ac',type='rectifier_ac')
				G.add_edge(x_num+'_ac',x_num,type='wire')

	#create edges w/ contactor
	for i in range(0,len(c_tups)):
		line = c_tups[i].split(' ')
		c_in_port = line[1]
		c_out_port = line[2]
		dummy_node_tups = []
		node_in = searchnode(c_in_port,g_tups,b_tups,t_tups,s_tups,dummy_node_tups,G)
		node_out = searchnode(c_out_port,g_tups,b_tups,t_tups,s_tups,dummy_node_tups,G)
		G.add_edges_from([(node_in,node_out),(node_out,node_in)],
			name=line[0],type=line[-1])

	#create edges w/o contactor, i.e. wire
	#assume only TRU, sensor, and generator can have a wire connected to other components
	for i in range(0,len(t_tups)):
		t_line = t_tups[i].split(' ')
		t_in_port = t_line[1]
		t_out_port = t_line[2]
		for j in range(0,len(b_tups)):
			b_line = b_tups[j].split(' ')
			if b_line[-1]=='AC':
				for k in range(1,len(b_line)-2):
					if t_in_port==b_line[k]:
						G.add_edges_from([(t_out_port+'_ac',b_line[-3]),
							(b_line[-3],t_out_port+'_ac')],type='wire')
						break
			if b_line[-1]=='DC':
				for k in range(1,len(b_line)-2):
					if t_out_port==b_line[k]:
						G.add_edges_from([(t_out_port,b_line[-3]),
							(b_line[-3],t_out_port)],type='wire')
						break
		for j in range(0,len(s_tups)):
			s_line = s_tups[j].split(' ')
			if t_in_port == s_line[2]:
				G.add_edges_from([(t_out_port+'_ac',s_line[2]),
					(s_line[2], t_out_port+'_ac')], type = 'wire')
			if t_out_port == s_line[1]:
				G.add_edges_from([(t_out_port,s_line[2]),
					(s_line[2], t_out_port)], type = 'wire')
		for j in range(0, len(g_tups)):
			g_line = g_tups[j].split(' ')
			if t_in_port == g_line[2]:
				G.add_edges_from([(t_out_port+'_ac',g_line[2]),
					(g_line[2], t_out_port+'_ac')], type = 'wire')
			if t_out_port == g_line[1]:
				G.add_edges_from([(t_out_port,g_line[2]),
					(g_line[2], t_out_port)], type = 'wire')
	# create wire connected to sensor
	for i in range(0, len(s_tups)):
		s_line = s_tups[i].split(' ')
		s_in_port = s_line[1]
		s_out_port = s_line[2]
		# when sensor is connected to bus
		for j in range(0, len(b_tups)):
			b_line = b_tups[j].split(' ')
			for k in range(1, len(b_line)-2):
				if s_in_port == b_line[k] or s_out_port == b_line[k]:
					G.add_edges_from([(s_out_port,b_line[-3]),
						(b_line[-3],s_out_port)], type = 'wire')
					break
		# when sensor is connected to generator
		for j in range(0, len(g_tups)):
			g_line = g_tups[j].split(' ')
			if s_in_port == g_line[2] or s_out_port == g_line[1]:
				G.add_edges_from([(g_line[2], s_out_port), 
					(s_out_port, g_line[2])], type = 'wire')
	# create wire connected to generator
	for i in range(0, len(g_tups)):
		g_line = g_tups[i].split(' ')
		g_in_port = g_line[1]
		g_out_port = g_line[2]
		# when generator is connected to bus
		for j in range(0, len(b_tups)):
			b_line = b_tups[j].split(' ')
			for k in range(1, len(b_line)-2):
				if g_in_port == b_line[k] or g_out_port == b_line[k]:
					G.add_edges_from([(g_out_port, b_line[-3]),
						(b_line[-3], g_out_port)], type = 'wire')
					break
	return G

#this function is only used by read_netlist
#if two nodes share one port which is not a components,
#define this node as this shared node + '_dummy'
def searchnode(port,g_tups,b_tups,t_tups,s_tups,dummy_node_tups,G):
	for i in range(0,len(g_tups)):
		line = g_tups[i].split(' ')
		g_out_port = line[2]
		if port==g_out_port:
			return g_out_port
	for i in range(0,len(b_tups)):
		line = b_tups[i].split(' ')
		for j in range(1,len(line)-2):
			if port==line[j]:
				return line[-3]
	for i in range(0,len(t_tups)):
		line = t_tups[i].split(' ')
		t_in_port = line[1]
		t_out_port = line[2]
		if port==t_in_port:
			return t_out_port+'_ac'
		if port==t_out_port:
			return t_out_port
	for i in range(0,len(s_tups)):
		line = s_tups[i].split(' ')
		s_out_port = line[2]
		if port==s_out_port:
			return s_out_port
	for i in range(0,len(dummy_node_tups)):
		line = dummy_node_tups[i].split('_')
		dummy_node = line[0]
	G.add_node(port+'_dummy',name = port+'dummy', type='dummy')
	dummy_node_tups.append(port+'_dummy')
	return port+'_dummy'

#only call this function at the very beginning to initialize
#produce declarations and also fill in uncon_comp_tups and contactor_tups
#uncon_comp_tups stands for uncontrollable compononent tups
def init(G, uncon_comp_tups, contactor_tups):
	nodes_number = G.nodes()
	edges_number = G.edges()
	node_name_data = nx.get_node_attributes(G, 'name')
	edge_name_data = nx.get_edge_attributes(G, 'name')
	edge_type_data = nx.get_edge_attributes(G, 'type')
	node_type_data = nx.get_node_attributes(G, 'type')
	declaration = '(set-option :print-success false)\n'
	declaration += '(set-option :produce-models true)\n(set-logic QF_UF)\n'
	for i in range(0, len(nodes_number)):
		x = nodes_number[i]
		node_type = node_type_data[x]
		if node_type != 'dummy':
			clause = '(declare-fun ' + node_name_data[x] + ' () Bool)\n'
			if node_type == 'generator' or node_type == 'APU' or node_type == 'rectifier_dc':
				uncon_comp_tups.append(node_name_data[x])
			declaration += clause
	for i in range(0, len(edges_number)):
		idx = edges_number[i]
		edge_type = edge_type_data[idx]
		if edge_type == 'contactor':
			edge_name = edge_name_data[idx]
			flag = 0
			for j in range(0, len(contactor_tups)):
				if edge_name == contactor_tups[j]:
					flag = 1
					break
			if flag == 0: contactor_tups.append(edge_name)
	for i in range(0, len(contactor_tups)):
		clause = '(declare-fun ' + contactor_tups[i] + ' () Bool)\n'
		declaration += clause
	return declaration

#no-paralleling for the two elements given
def no_paralleling(node1, node2, G):
	nodes_number = G.nodes()
	edge_type_data = nx.get_edge_attributes(G,'type')
	node_name_data = nx.get_node_attributes(G,'name')
	edge_name_data = nx.get_edge_attributes(G,'name')
	num1 = num2 = 0
	for i in range(0, len(nodes_number)):
		x = nodes_number[i]
		if node_name_data[x] == node1:
			num1 = x
		elif node_name_data[x] == node2:
			num2 = x
	#check if components are valid
	if num1 == 0: 
		print 'Error: ' + node1 + ' Not Found'
		exit()
	if num2 == 0: 
		print 'Error: ' + node2 + ' Not Found' 
		exit()
	tups = list(nx.all_simple_paths(G, num1, num2)) # find all the simple paths connecting num1 and num2
	clause = '(assert (not'
	if len(tups)>1: clause += ' (or' # if more than one simple paths
	if tups != []:
		for k in range(0,len(tups)):
			clause += ' (and'
			one_path = tups[k]
			for x in range(0,len(one_path)-1):
				if edge_type_data[(one_path[x],one_path[x+1])]=='contactor':
					clause += ' ' + edge_name_data[(one_path[x],one_path[x+1])]
			clause += ')'
		if len(tups)>1: clause += ')))\n'
		else: clause += '))\n'
	return clause

#no-paralleling for any two elements in name_tups provided by the user
def no_paralleling_set(name_tups, G):
	nodes_number = G.nodes()
	edge_type_data = nx.get_edge_attributes(G,'type')
	node_name_data = nx.get_node_attributes(G,'name')
	edge_name_data = nx.get_edge_attributes(G,'name')
	num_tups = []
	for i in range(0, len(name_tups)):
		for j in range(0, len(nodes_number)):
			x = nodes_number[j]
			if node_name_data[x] == name_tups[i]:
				num_tups.append(x)
		#check if there's invalid input component       
		if j == len(nodes_number):
			print 'Error: Component ' + e_bus_list[i] + ' Not Found'
			exit()
	specs_assert = ''
	for i in range(0, len(num_tups)-1):
		for j in range(i+1, len(num_tups)):
			tups = list(nx.all_simple_paths(G, num_tups[i], num_tups[j]))
			clause = '(assert (not'
			if len(tups)>1: clause += ' (or'
			if tups != []:
				for k in range(0,len(tups)):
					clause += ' (and'
					one_path = tups[k]
					for x in range(0,len(one_path)-1):
						if edge_type_data[(one_path[x],one_path[x+1])]=='contactor':
							clause += ' ' + edge_name_data[(one_path[x],one_path[x+1])]
					clause += ')'
				if len(tups)>1: clause += ')))\n'
				else: clause += '))\n'
			specs_assert += clause
	return specs_assert

#essential buses must be powered on at all time
def always_powered_on(e_bus_list, G):
	nodes_number = G.nodes()
	edge_type_data = nx.get_edge_attributes(G,'type')
	node_name_data = nx.get_node_attributes(G,'name')
	node_type_data = nx.get_node_attributes(G,'type')
	edge_name_data = nx.get_edge_attributes(G,'name')
	type_data = nx.get_node_attributes(G,'type')
	generator_list = []
	apu_list = []
	for i in range(0,nx.number_of_nodes(G)):
		x = nodes_number[i]
		if type_data[x]=='generator':
			generator_list.append(x)
		elif type_data[x]=='APU':
			apu_list.append(x)
	e_bus_num = []
	for i in range(0, len(e_bus_list)):
		for j in range(0, len(nodes_number)):
			x = nodes_number[j]
			if node_name_data[x] == e_bus_list[i]:
				e_bus_num.append(x)
				break
	#check if there's invalid input component       
		if j == len(nodes_number):
			print 'Error: Component ' + e_bus_list[i] + ' Not Found'
			exit()
	specs_assert = ''
	for i in range(0,len(e_bus_num)):
		bus_name = node_name_data[e_bus_num[i]]
		clause = '(assert (= ' + bus_name + '(or '
		for j in range(0,len(generator_list)):
			tups = list(nx.all_simple_paths(G,generator_list[j],e_bus_num[i]))  
			for k in range(0,len(tups)):
				#add nodes along the path to the clause
				#add edges that have contactor to the clause
				clause += '(and'
				one_path = tups[k]
				for x in range(0,len(one_path)-1):
					if node_type_data[one_path[x]]!='dummy':
						clause += ' ' + node_name_data[one_path[x]]
					if edge_type_data[(one_path[x],one_path[x+1])]=='contactor':
						clause += ' ' + edge_name_data[(one_path[x],one_path[x+1])]
				clause += ')'
		if len(apu_list) != 0:
			for l in range(0,len(apu_list)):
				tups = list(nx.all_simple_paths(G,apu_list[l],e_bus_num[i]))    
				for k in range(0,len(tups)):
					#add nodes along the path to the clause
					#add edges that have contactor to the clause
					clause += '(and'
					one_path = tups[k]
					for x in range(0,len(one_path)-1):
						if node_type_data[one_path[x]]!='dummy':
							clause += ' ' + node_name_data[one_path[x]]
						if edge_type_data[(one_path[x],one_path[x+1])]=='contactor':
							clause += ' ' + edge_name_data[(one_path[x],one_path[x+1])]
					clause += ')'       
		clause += ')))\n'
		specs_assert += clause
	clause = '(assert (and'
	for i in range(0, len(e_bus_num)):
		bus_name = node_name_data[e_bus_num[i]]
		clause += ' ' + bus_name
	clause += '))\n'
	specs_assert += clause
	return specs_assert

#at least one generator or APU is healthy
#this function will give a general assumption on the condition
#of generators
def generator_healthy(G):
	g_list = generator_list(G)
	clause = '(assert (or'
	for g in g_list:
		clause += ' ' + g
	clause += '))\n'
	return clause

#at least one rectifier is healthy
#this function will give a general assumption on the condition
#of generators
def rectifier_healthy(G):
	all_rectifiers = rectifier_list(G)
	clause = '(assert (or'
	for r in all_rectifiers:
		clause += ' ' + r + '_dc'
	clause += '))\n'
	return clause

#all the sensors are healthy
#this function will give a general assumption on the condition
#of sensors
def sensor_healthy(G):
	s_list = sensor_list(G)
	clause = '(assert (and'
	for s in s_list:
		clause += ' ' + s
	clause += '))\n'
	return clause

#equivalent the ac part and dc part of a rectifier
#in other words, treat them as equal everywhere
def rect_ac_dc_equ(G):
	all_rectifiers = rectifier_list(G)
	specs_assert = ''

	for r in all_rectifiers:
		clause = '(assert (='
		r_dc_name = r + '_dc'
		r_ac_name = r + '_ac'
		clause += ' ' + r_ac_name + ' ' + r_dc_name + '))\n'
		specs_assert += clause

	return specs_assert

#allow user to set values of controllable components
#if value == 1, then set component to be true
#if value == 0, then set component to be false
def setValue(component, value, G):
	if component[0] == 'T':
		component += '_dc'
	if value == 1:
		clause = '(assert ' + component + ')\n'
	elif value == 0:
		clause = '(assert (not ' + component + '))\n'
	return clause

#if a component (not a contactor) turns unhealthy, 
#open all contactors next to it
#include this in advance if such a component turning 
#unhealthy would affect the functioning of circuit
def isolate(component, G):
	nodes_number = G.nodes()
	edges_number = G.edges()
	edge_type_data = nx.get_edge_attributes(G,'type')
	node_name_data = nx.get_node_attributes(G,'name')
	edge_name_data = nx.get_edge_attributes(G,'name')
	comp2 = component
	if component[0] == 'T':
		comp1 = component + '_ac'
		comp2 = component + '_dc'
	comp_num1 = comp_num2 = comp_num = 0
	for i in range(0, len(nodes_number)):
		x = nodes_number[i]
		if component[0] != 'T' and node_name_data[x] == component:
			comp_num = x
			break
		elif component[0] == 'T' and node_name_data[x] == comp2:
			comp_num2 = x
			comp_num1 = x + '_ac'
			break
	if i == len(nodes_number):
		print 'Error: ' + component + ' Not Found'
		exit()
	neighbor_idx = []
	if component[0] != 'T':
		for i in range(0, len(edges_number)):
			if edges_number[i][0] == comp_num:
				neighbor_idx.append(edges_number[i])
	else:
		for i in range(0, len(edges_number)):
			if edges_number[i][0] == comp_num1 or edges_number[i][0] == comp_num2:
				neighbor_idx.append(edges_number[i])
	contactor_tups = []
	for i in range(0, len(neighbor_idx)):
		idx = neighbor_idx[i]
		if edge_type_data[idx] == 'contactor':
			edge_name = edge_name_data[idx]
			contactor_tups.append(edge_name)
	if len(contactor_tups) == 0:
		clause = ''
		return clause
	clause = '(assert (=> (not ' + comp2 + ')'
	if len(contactor_tups) > 1:
		clause += ' (and '
	for i in range(0, len(contactor_tups)):
		clause += '(not ' + contactor_tups[i] + ')'
	if len(contactor_tups) > 1:
		clause += ')))\n'   
	elif len(contactor_tups) == 1:
		clause += '))\n'
	return clause

#APUs should only be turned on if some or all generators go unhealthy
#Only use this function if there are any APUs
def generator_priority(G):
	nodes_number = G.nodes()
	node_name_data = nx.get_node_attributes(G,'name')
	type_data = nx.get_node_attributes(G,'type')
	generator_list = []
	APU_list = []
	for i in range(0,nx.number_of_nodes(G)):
		x = nodes_number[i]
		if type_data[x]=='generator':
			generator_list.append(x)
		elif type_data[x]=='APU':
			APU_list.append(x)
	if len(APU_list) == 0:
		return
	clause = '(assert (=> '
	if len(generator_list) > 1:
		clause += '(and'
	for i in range(0, len(generator_list)):
		g_name = node_name_data[generator_list[i]]
		clause += ' ' + g_name
	clause += ') '
	if len(APU_list) > 1:
		clause += '(and '
	for i in range(0, len(APU_list)):
		apu_name = node_name_data[APU_list[i]]
		clause +=  '(not ' + apu_name + ')'
	clause += ')))\n'
	return clause

# For simplicity in GUI purpose
def isolate_all(isolate_list, G):
	specs_assert = ''
	for elt in isolate_list:
		specs_assert += isolate(elt, G)
	return specs_assert

# returns a tup of names of generators
def generator_list(G):
	nodes_number = G.nodes()
	node_name_data = nx.get_node_attributes(G,'name')
	type_data = nx.get_node_attributes(G,'type')
	all_generators = []
	for i in range(0,nx.number_of_nodes(G)):
		x = nodes_number[i]
		if type_data[x]=='generator':
			all_generators.append(node_name_data[x])
	return all_generators

# returns a tup of names of buses
def bus_list(G):
	nodes_number = G.nodes()
	node_name_data = nx.get_node_attributes(G,'name')
	type_data = nx.get_node_attributes(G,'type')
	all_buses = []
	for i in range(0,nx.number_of_nodes(G)):
		x = nodes_number[i]
		if type_data[x]=='bus':
			all_buses.append(node_name_data[x])
	return all_buses

# returns a tup of names of rectifiers
# like T1, T2
def rectifier_list(G):
	nodes_number = G.nodes()
	node_name_data = nx.get_node_attributes(G,'name')
	type_data = nx.get_node_attributes(G,'type')
	all_rectifiers = []
	for i in range(0,nx.number_of_nodes(G)):
		x = nodes_number[i]
		if type_data[x]=='rectifier_dc':
			dc_name = node_name_data[x]
			all_rectifiers.append(dc_name[:-3])
	return all_rectifiers

# returns a tup of names of sensors
def sensor_list(G):
	nodes_number = G.nodes()
	node_name_data = nx.get_node_attributes(G, 'name')
	type_data = nx.get_node_attributes(G, 'type')
	all_sensors = []
	for i in range(0, nx.number_of_nodes(G)):
		x = nodes_number[i]
		if type_data[x] =='sensor':
			all_sensors.append(node_name_data[x])
	return all_sensors

# returns measurements of sensor given values
def sensor_measurement(G, uncon_comp_tups, contactor_tups, states):
	sensor = {}
	# Check whether there are enough states
	for i in range (0, len(uncon_comp_tups)):
		uncon_name = uncon_comp_tups[i]
		if uncon_name[0] == 'T':
			uncon_name = ''
			for j in range (0, len(uncon_comp_tups[i])-3):
				uncon_name += uncon_comp_tups[i][j]
		if states.has_key(uncon_name) == False:
			print 'Error: ' + uncon_name + ' Not Found'
			exit()
	for i in range (0, len(contactor_tups)):
		contactor_name = contactor_tups[i]
		if states.has_key(contactor_name) == False:
			print 'Error: ' + contactor_name + ' Not Found'
			exit()

	# Delete all the edges if open and the nodes connected to them
	# Do not delete sensors
	H = G.copy()
	edges_number = H.edges()
	edge_name_data = nx.get_edge_attributes(H, 'name')
	for i in edges_number:
		name = ''
		if edge_name_data.has_key(i) == True:
			name = edge_name_data[i]
			if states[name] == 0:
				H.remove_edge(i[0], i[1])
	
	# Find all the sensors and generators
	nodes_number = H.nodes()
	node_type_data = nx.get_node_attributes(H, 'type')
	g_list = []
	s_list = []
	for i in range (0, len(nodes_number)):
		x = nodes_number[i]
		if node_type_data[x] == 'generator':
			g_list.append(x)
		elif node_type_data[x] == 'sensor':
			s_list.append(x)

	# Check every sensor
	for i in range (0, len(s_list)):
		healthy = 1
		target = s_list[i]
		# Check sensor[i] with every generator
		for j in range (0, len(g_list)):
			source = g_list[j]
			paths = list(nx.all_simple_paths(H, source, target))
			# Check every path between sensor[i] and generator[j]
			for k in range (0, len(paths)):
				path = paths[k]
				connect = 1
				# Check whether this path is connected
				for l in range (0, len(path) - 1):
					element = path[l]
					# Check every edge
					if H.edge[element][path[l+1]]['type'] == 'contactor':
						if states[H.edge[path[l]][path[l+1]]['name']] == 0:
							connect = 0
				# if there is a live path
				if connect == 1:
					# Check every node
					for l in range (0, len(path) - 1):
						element = path[l]
						if H.node[element]['type'] == 'generator':
							if states[H.node[element]['name']] == 0:
								healthy = 0
						elif H.node[element]['type'] == 'APU':
							if states[H.node[element]['name']] == 0:
								healthy = 0
						elif H.node[element]['type'] == 'rectifier_dc' or H.node[element]['type'] == 'rectifier_ac':
							rectifier_name = ''
							for m in range (0, len(H.node[element]['name'])-3):
								rectifier_name += H.node[element]['name'][m]
							if states[rectifier_name] == 0:
								healthy = 0
		sensor[H.node[target]['name']] = healthy
	return sensor

# return a list of compatible states with given sensor readings and controllable contactors
def compatible_states(G, sensor_readings, con_cont):
	uncon_comp_tups = []
	contactor_tups = []
	declaration = init(G, uncon_comp_tups, contactor_tups)

	compatible_list = []
	elements = []
	initial_state = con_cont.copy()
	for i in range (0, len(uncon_comp_tups)):
		name = ''
		if uncon_comp_tups[i][0] == 'T':
			for j in range (0, len(uncon_comp_tups[i])-3):
				name += uncon_comp_tups[i][j]
		else:
			name = uncon_comp_tups[i]
		elements.append(name)
	for i in range (0, len(contactor_tups)):
		if con_cont.has_key(contactor_tups[i]) == 0:
			elements.append(contactor_tups[i])

	num_state = pow(2, len(elements))
	for i in range (0, num_state):
		state = initial_state
		value = format(i, '0' + str(len(elements)) + 'b')
		for j in range (0, len(value)):
				state[elements[j]] = int(value[j])
		test_readings = sensor_measurement(G, uncon_comp_tups, contactor_tups, state)
		if test_readings == sensor_readings:
			state.update(sensor_readings)
			compatible_list.append(state.copy())
	return compatible_list

# return a list of compatible states with given sensor readings and controllable contactors
def compatible_states_without_sensors(G, sensor_readings, con_cont):
	uncon_comp_tups = []
	contactor_tups = []
	declaration = init(G, uncon_comp_tups, contactor_tups)

	compatible_list = []
	elements = []
	initial_state = con_cont.copy()
	for i in range (0, len(uncon_comp_tups)):
		name = ''
		if uncon_comp_tups[i][0] == 'T':
			for j in range (0, len(uncon_comp_tups[i])-3):
				name += uncon_comp_tups[i][j]
		else:
			name = uncon_comp_tups[i]
		elements.append(name)
	for i in range (0, len(contactor_tups)):
		if con_cont.has_key(contactor_tups[i]) == 0:
			elements.append(contactor_tups[i])

	num_state = pow(2, len(elements))
	for i in range (0, num_state):
		state = initial_state
		value = format(i, '0' + str(len(elements)) + 'b')
		for j in range (0, len(value)):
				state[elements[j]] = int(value[j])
		test_readings = sensor_measurement(G, uncon_comp_tups, contactor_tups, state)
		if test_readings == sensor_readings:
			compatible_list.append(state.copy())
	return compatible_list

# create the database of all the states, and create the csv file
def generate_database_csv(G, write_file_name):
	uncon_comp_tups = []
	contactor_tups = []
	declaration = init(G, uncon_comp_tups, contactor_tups)

	with open(write_file_name, 'w') as csvfile:
		for i in range(0, pow(2, len(uncon_comp_tups) + len(contactor_tups))):
			index = 0
			states = {}
			states_value = format(i, '0' + str(len(uncon_comp_tups) + len(contactor_tups)) + 'b')
			for j in uncon_comp_tups:
				if j[0] == 'T':
					name = ''
					for k in range(0, len(j) - 3):
						name += j[k]
					states[name] = int(states_value[index])
				else:
					states[j] = int(states_value[index])
				index += 1
			for j in contactor_tups:
				states[j] = int(states_value[index])
				index += 1
			states_copy = states.copy()
			sensor_readings = sensor_measurement(G, uncon_comp_tups, contactor_tups, states_copy)
			states.update(sensor_readings)
			if i == 0:
				fieldnames = list(states)
				writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
				writer.writeheader()
			writer.writerow(states)

	return 0

# read a set of compatible states from database
def get_compatible_states_from_database(read_file_name, sensor_readings, con_cont):
	compatible_list = []
	sensors = sensor_readings.keys()
	contactors = con_cont.keys()

	with open(read_file_name) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			choose_it = True
			for i in range (0, len(row)):
				number = int(row[list(row)[i]])
				row[list(row)[i]] = number
			if len(sensor_readings) > len(con_cont):
				for i in range (0, len(sensors)):
					if row[sensors[i]] != sensor_readings[sensors[i]]:
						choose_it = False
						break
				if choose_it == True:
					for i in range (0, len(contactors)):
						if row[contactors[i]] != con_cont[contactors[i]]:
							choose_it = False
							break
			else:
				for i in range (0, len(contactors)):
					if row[contactors[i]] != con_cont[contactors[i]]:
						choose_it = False
						break
				if choose_it == True:
					for i in range (0, len(sensors)):
						if row[sensors[i]] != sensor_readings[sensors[i]]:
							choose_it = False
							break
			if choose_it == True:
				compatible_list.append(row)

	return compatible_list

# Functions below are for the greedy algorithm
# This function generates the database in the sequence according to sensor readings
# create the database of all the states, this is used to create the csv file
def generate_database(G, sensors, con_conts, write_file_name):
	compatible_database = []
	sensor_dict = {}
	cc_dict = {}

	with open(write_file_name, 'wb') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
		for i in range (0, pow(2, len(sensors))):
			sensors_value = format(i, '0' + str(len(sensors)) + 'b')
			for j in range (0, len(sensors)):
				sensor_dict[sensors[j]] = int(sensors_value[j])
			for j in range (0, pow(2, len(con_conts))):
				cont_value = format(j, '0' + str(len(con_conts)) + 'b')
				for k in range (0, len(con_conts)):
					cc_dict[con_conts[k]] = int(cont_value[k])
				temp_list = compatible_states(G, sensor_dict, cc_dict)
				for k in temp_list:
					for l in sensor_dict:
						k.pop(l)
					for l in cc_dict:
						k.pop(l)
				if (len(temp_list) > 0):
					row = [sensor_dict, cc_dict]
					row.extend(temp_list)
					spamwriter.writerow(row)
					compatible_database.append(temp_list)

	return compatible_database

# create a csv file storing all the compatible states
def generate_database_in_csv(database, write_file_name):
	with open(write_file_name, 'w') as csvfile:
		if len(database) > 0:
			fieldnames = list(database[0][0])
		else:
			print 'Error: empty database'
			exit()
		writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
		writer.writeheader()

		for i in range (0, len(database)):
			for j in range (0, len(database[i])):
				row = database[i][j]
				writer.writerow(row)

	return 0

# read the compatible states from the database
def read_from_database(read_file_name, sensor_readings, con_cont):
	compatible_list = []

	with open(read_file_name, 'rb') as f:
	    reader = csv.reader(f)
	    for row in reader:
	    	if ast.literal_eval(row[0]) == sensor_readings:
	    		if ast.literal_eval(row[1]) == con_cont:
	    			for i in range(2, len(row)):
	    				compatible_list.append(ast.literal_eval(row[i]))

	return compatible_list

def assign_false_values(a_dict, a_list):
	for i in a_list:
		if a_dict[i] == 0:
			a_dict[i] = 1
		else:
			a_dict[i] = 0

	return a_dict

def sensors_not_connected_with_generators(G, con_conts):
	known_sensors = []

	# delete all edges with controllable contactors
	H = G.copy()
	edges_number = H.edges()
	edge_name_data = nx.get_edge_attributes(H, 'name')
	for i in edges_number:
		name = ''
		if edge_name_data.has_key(i) == True:
			name = edge_name_data[i]
			if con_conts.count(name) > 0:
				H.remove_edge(i[0], i[1])
	
	# Find all the sensors and generators
	nodes_number = H.nodes()
	node_type_data = nx.get_node_attributes(H, 'type')
	g_list = []
	s_list = []
	for i in range (0, len(nodes_number)):
		x = nodes_number[i]
		if node_type_data[x] == 'generator':
			g_list.append(x)
		elif node_type_data[x] == 'sensor':
			s_list.append(x)

	# Check every sensor
	for i in range (0, len(s_list)):
		target = s_list[i]
		flag = 0
		# Check sensor[i] with every generator
		for j in range (0, len(g_list)):
			source = g_list[j]
			paths = list(nx.all_simple_paths(H, source, target))
			if len(paths) > 0:
				flag = 1
		if flag == 0:
			known_sensors.append(H.node[target]['name'])

	return known_sensors

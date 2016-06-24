from greedy import *
import time

filename = 'circuit_sensor_1.net'
read_file_name = 'database1.csv'
G = nx.DiGraph()
G = read_netlist(filename)
uncon_comp_tups = []
contactor_tups = []
declaration = init(G, uncon_comp_tups, contactor_tups)

'''
sensors = ['S1', 'S2']
con_conts = ['C1', 'C3', 'C4', 'C6']
result = generate_database(G, sensors, con_conts, 'database1.csv')
'''

actual_state = {'G2': 1, 'G1': 0, 'T2': 0, 'T1': 0, 'C2': 0, 'C5': 1}

for j in range(0, pow(2, len(actual_state))):
	# set the actual state
	state_value = format(j, '0' + str(len(actual_state)) + 'b')
	for i in range(0, len(actual_state)):
		actual_state[list(actual_state)[i]] = int(state_value[i])

	action = {'C1': 1, 'C3': 1, 'C4': 1, 'C6': 1}
	action_list = [action.copy()]
	states = actual_state.copy()
	states.update(action)

	sensor_readings = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)
	compatible_states = read_from_database(read_file_name, sensor_readings, action)

	while (len(compatible_states) > 1 or len(compatible_states) == 0):
		sensor_readings = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)
		compatible_states_candidate = read_from_database(read_file_name, sensor_readings, action)
		temp_states = []
		if len(compatible_states) == 0:
			compatible_states = compatible_states_candidate
		else:
			for i in compatible_states:
				if compatible_states_candidate.count(i) > 0:
					temp_states.append(i.copy())
			compatible_states = list(temp_states)

		if len(action_list) == 6: break
		action = build_tree(G, read_file_name, compatible_states, action_list)
		states.update(action)
		action_list.append(action.copy())

	print len(compatible_states)
from greedy import *
import time

filename = 'circuit_sensor_1_more_sensor.net'
read_file_name = 'database1_more_sensor.csv'
G = nx.DiGraph()
G = read_netlist(filename)
uncon_comp_tups = []
contactor_tups = []
declaration = init(G, uncon_comp_tups, contactor_tups)
fail_sensors = ['S1', 'S2']

'''
sensors = ['S1', 'S2', 'S3']
con_conts = ['C1', 'C3', 'C4', 'C6']
result = generate_database(G, sensors, con_conts, read_file_name)
'''

actual_state = {'G2': 1, 'G1': 0, 'T2': 0, 'T1': 0, 'C2': 0, 'C5': 1}

for j in range(0, pow(2, len(actual_state))):
	# set up the actual state
	state_value = format(j, '0' + str(len(actual_state)) + 'b')
	for i in range(0, len(actual_state)):
		actual_state[list(actual_state)[i]] = int(state_value[i])
	print 'actual: '
	print actual_state

	# set up the initial action
	action = {'C1': 1, 'C3': 1, 'C4': 1, 'C6': 1}
	action_list = [action.copy()]
	states = actual_state.copy()
	states.update(action)

	# create a set contains compatible state sets when sensor is faulty or not
	compatible_states = []
	for i in range(0, pow(2, len(fail_sensors))):
		compatible_states.append([])

	count = 0
	while (len(compatible_states) >= 0):
		sensor_readings = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)
		assign_false_values(sensor_readings, ['S1']) # readings given by the circuit

		# consider all the cases when some sensors are faulty
		compatible_states_candidate = []
		for i in range(0, len(compatible_states)):
			# set up the conditions, where 1 represents healthy, 0 represents faulty
			condition = format(i, '0' + str(len(fail_sensors)) + 'b')
			# compatible_states_candidates contains all the states given sensor readings with
			# all possible health conditions
			temp_readings = sensor_readings.copy()
			for k in range(0, len(fail_sensors)):
				if int(condition[k]) == 0: 
					if temp_readings[fail_sensors[k]] == 0:
						temp_readings[fail_sensors[k]] = 1
					else:
						temp_readings[fail_sensors[k]] = 0
			compatible_states_candidate.append(read_from_database(read_file_name, temp_readings, action))
		temp_states = []
		for i in range(0, pow(2, len(fail_sensors))):
			temp_states.append([])
		if count == 0:
			compatible_states = compatible_states_candidate
		else:
			for i in range(0, len(compatible_states)):
				for k in compatible_states[i]:
					if compatible_states_candidate[i].count(k) > 0:
						temp_states[i].append(k.copy())
			compatible_states = list(temp_states)

		if len(action_list) == 6: break
		action = build_tree(G, read_file_name, compatible_states, action_list, fail_sensors)
		if action == {}: break
		states.update(action)
		action_list.append(action.copy())
		print action
		count += 1

	for i in compatible_states:
		print i
	print '---'
	if j == 2: break
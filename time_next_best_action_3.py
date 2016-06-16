from greedy import *
import time

filename = 'circuit_sensor_3.net'
G = nx.DiGraph()
G = read_netlist(filename)
uncon_comp_tups = []
contactor_tups = []
declaration = init(G, uncon_comp_tups, contactor_tups)
actual_state = {'G2': 1, 'G1': 1, 'G3': 1, 'G4': 1, 'T2': 0, 'T1': 0, 'C2': 0, 'C5': 1, 'C7': 1, 'C8': 0, 'C10': 1}

for j in range(0, pow(2, len(actual_state))):
	# set the actual state
	state_value = format(j, '0' + str(len(actual_state)) + 'b')
	for i in range(0, len(actual_state)):
		actual_state[list(actual_state)[i]] = int(state_value[i])

	# test the greedy strategy
	# set the actual state and initial action
	# get the initial sensor readings
	read_file_name = 'database3.csv'
	action = {'C1': 1, 'C3': 1, 'C4': 1, 'C6': 1, 'C2': 1, 'C9': 1}
	action_list = [action.copy()]
	states = actual_state.copy()
	states.update(action)

	# set the initial compatible_states to be all states
	compatible_states = []
	with open(read_file_name, 'rb') as f:
		reader = csv.reader(f)
		for row in reader:
			for i in range(2, len(row)):
				candidate = ast.literal_eval(row[i])
				if compatible_states.count(candidate) == 0:
					compatible_states.append(candidate)

	while (len(compatible_states) > 1):
		sensor_readings = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)
		compatible_states_candidate = read_from_database(read_file_name, sensor_readings, action)
		temp_states = []
		for i in compatible_states:
			if compatible_states_candidate.count(i) > 0:
				temp_states.append(i.copy())
		compatible_states = list(temp_states)

		# if all the actions are performed, then break
		if len(action_list) == 6: break

		# find the best action to perform
		start = time.time()
		action = find_best_action(sensor_readings, compatible_states, G, read_file_name, action_list)
		end = time.time()
		print end - start
		states.update(action)
		action_list.append(action.copy())
	'''
	print 'All possible states are:'
	for i in compatible_states:
		print i
	'''
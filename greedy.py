from specs import *

def find_best_action(sensor_readings, compatible_states, G, read_file_name, action_list):
	uncon_comp_tups = []
	contactor_tups = []
	declaration = init(G, uncon_comp_tups, contactor_tups)

	best_action = {}
	action = {}
	initial_action = action_list[0]
	smallest_num_compatible_states = len(compatible_states)

	# for all actions
	for i in range(0, pow(2, len(initial_action))):
		# print 'i: ' + str(i)
		action_value = format(i, '0' + str(len(initial_action)) + 'b')
		for j in range(0, len(initial_action)):
			action[list(initial_action)[j]] = int(action_value[j])
		if action_list.count(action) > 0: continue

		# for all compatible states
		for j in range(0, len(compatible_states)):
			# find potential sensor readings
			states = compatible_states[j].copy()
			states.update(action)
			readings = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)
			compatible_states_candidate = read_from_database(read_file_name, readings, action)
			compatible_intersection = []
			for k in compatible_states:
				if compatible_states_candidate.count(k) > 0:
					compatible_intersection.append(k)
			if len(compatible_intersection) <= smallest_num_compatible_states:
				best_action = action.copy()
				smallest_num_compatible_states = len(compatible_intersection)

	return best_action

def build_tree(G, read_file_name, compatible_states, action_list):
	action = action_list[0].copy()
	sensors = sensor_list(G)
	sensor_readings = {}
	factor = -1
	for i in range(0, pow(2, len(action))):
		action_value = format(i, '0' + str(len(action)) + 'b')
		for j in range(0, len(action)):
			action[list(action)[j]] = int(action_value[j])
		if action_list.count(action) > 0: continue

		current_factor = 0
		for j in range(0, pow(2, len(sensors))):
			sensor_value = format(j, '0' + str(len(sensors)) + 'b')
			for k in range(0, len(sensors)):
				sensor_readings[sensors[k]] = int(sensor_value[k])
			count = 0
			compatible_states_candidate = read_from_database(read_file_name, sensor_readings, action)
			for k in compatible_states_candidate:
				if compatible_states.count(k) > 0:
					count += 1
			current_factor += float(count*count)/len(compatible_states)

		if factor == -1:
			factor = current_factor
			best_action = action.copy()
		else:
			if current_factor < factor:
				factor = current_factor
				best_action = action.copy()

	return best_action

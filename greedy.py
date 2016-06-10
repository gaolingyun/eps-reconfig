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

from specs import *

def find_best_action(sensor_readings, compatible_states, G, read_file_name, action_list):
	uncon_comp_tups = []
	contactor_tups = []
	declaration = init(G, uncon_comp_tups, contactor_tups)

	best_action = {}
	action = {}
	initial_action = action_list[0]
	smallest_max = len(compatible_states)

	# for all actions
	#print 'test action:'
	for i in range(0, pow(2, len(initial_action))):
		# print 'i: ' + str(i)
		action_value = format(i, '0' + str(len(initial_action)) + 'b')
		for j in range(0, len(initial_action)):
			action[list(initial_action)[j]] = int(action_value[j])
		if action_list.count(action) > 0: continue
		#print action

		max_num_compatible_states = 0
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
			if len(compatible_intersection) > max_num_compatible_states:
				max_num_compatible_states = len(compatible_intersection)
		#print max_num_compatible_states

		if max_num_compatible_states < smallest_max:
			best_action = action.copy()
			smallest_max = max_num_compatible_states

	return best_action

def build_tree(G, read_file_name, compatible_states, action_list, fail_sensors):
	action = action_list[0].copy()
	sensors = sensor_list(G)
	healthy_sensors = list(sensors)
	sensor_readings = {}
	factor = -1
	for i in fail_sensors:
		healthy_sensors.remove(i)

	for i in range(0, pow(2, len(action))):
		action_value = format(i, '0' + str(len(action)) + 'b')
		for j in range(0, len(action)):
			action[list(action)[j]] = int(action_value[j])
		if action_list.count(action) > 0: continue

		current_factor = 0
		for j in range(0, pow(2, len(healthy_sensors))):
			sensor_value = format(j, '0' + str(len(healthy_sensors)) + 'b')
			for k in range(0, len(healthy_sensors)):
				sensor_readings[healthy_sensors[k]] = int(sensor_value[k])
			count = 0
			compatible_states_candidate = []
			for k in range(0, pow(2, len(fail_sensors))):
				reading_value = format(k, '0' + str(len(fail_sensors)) + 'b')
				for l in range(0, len(fail_sensors)):
					sensor_readings[fail_sensors[l]] = int(reading_value[l])
				compatible_states_candidate.extend(read_from_database(read_file_name, sensor_readings, action))
			for k in range(0, len(compatible_states)):
				for l in compatible_states[k]:
					if compatible_states_candidate.count(l) > 0:
						count += 1
			if len(fail_sensors) == 0:
				current_factor += float(count*count)/len(compatible_states[0])
			else:
				if current_factor < count:
					current_factor = count

		#print current_factor
		if factor == -1:
			factor = current_factor
			best_action = action.copy()
		else:
			if current_factor < factor:
				factor = current_factor
				best_action = action.copy()

	if len(fail_sensors) == 0:
		if factor == len(compatible_states[0]): best_action = {}
	else:
		total_states = 0
		for i in compatible_states:
			total_states += len(i)
		if total_states == factor: best_action = {}

	return best_action

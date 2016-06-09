from specs import *

# implement the greedy strategy
def find_state(G, actual_state, initial_action, initial_reading, read_file_name):
	action = initial_action.copy()
	uncon_comp_tups = []
	contactor_tups = []
	declaration = init(G, uncon_comp_tups, contactor_tups)
	compatible = read_from_database(read_file_name, initial_reading, initial_action)
	num_action = 1
	print len(compatible)

	while (num_action < pow(2, len(initial_action)) and len(compatible) > 1):
		# for all actions v
		num_action += 1
		s_length = len(compatible)
		better_action = {}
		for i in range(0, pow(2, len(action))):
			action_value = format(i, '0' + str(len(initial_action)) + 'b')
			for j in range(0, len(action)):
				action[list(action)[j]] = int(action_value[j])
			if action == initial_action:
				continue
			# for all compatible states
			for j in range(0, len(compatible)):
				# find potential sensor reading
				states = compatible[j].copy()
				states.update(action)
				y = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)
				s = read_from_database(read_file_name, y, action)
				s_next = []
				for k in compatible:
					if s.count(k) > 0:
						s_next.append(k)
				if j == 0:
					length = len(s_next)
				else:
					if length > len(s_next):
						length = length
					else:
						length = len(s_next)
			if len(better_action) == 0:
				better_action = action
			else:
				if length <= s_length:
					better_action = action.copy()
					s_length = length

		states = actual_state.copy()
		states.update(better_action)
		reading_new = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)
		compatible_new = read_from_database(read_file_name, reading_new, better_action)
		compatible_temp = []
		for i in compatible:
			if compatible_new.count(i) > 0:
				compatible_temp.append(i)
		compatible = compatible_temp

	return compatible
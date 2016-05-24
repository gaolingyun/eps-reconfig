from test import *

''' This can be used when generate_random_circuit is available
num_comp = [4, 10, 20]
ratio_sensor_comp = [0.10, 0.25, 0.50]
ratio_cc = [0.50]

for i in num_comp:
	for j in ratio_sensor_comp:
		for k in ratio_cc:
			# generate a random circuit
			G = generate_random_circuit(i, j)
			# generate database
			sensors = sensor_list(G)
			con_conts = generate_random_cc(G, k)
			database = generate_database(G, sensors, con_conts)
			generate_database_in_csv(database, 'database.csv')

			direct_time = []
			csv_time = []
			for l in range (0, 10):
				sensor_readings = generate_dict(sensors)
				C_c = generate_dict(con_conts)
				# time used by directly getting compatible states
				start = time.time()
				states1 = compatible_states(G, sensor_readings, C_c)
				end = time.time()
				direct_time.append(end - start)
				# time used by reading from database
				start = time.time()
				states2 = get_compatible_states_from_database('database.csv', sensor_readings, C_c)
				end = time.time()
				csv_time.append(end - start)
				# verification
				verifier(states1, states2)
			average_time_1 = sum(direct_time)/len(direct_time)
			average_time_2 = sum(csv_time)/len(csv_time)
			print 'number of components: ' + str(i)
			print '--ratio between sensor and components: ' + str(j)
			print '----ratio of controllable contactors: ' + str(k)
			print '------direct: ' + str(average_time_1)
			print '------read: ' + str(average_time_2)
'''

# This is a test for the codes above

filename = 'circuit_sensor_2.net'
G = nx.DiGraph()
G = read_netlist(filename)
sensors = sensor_list(G)
print sensors
con_conts = generate_random_cc(G, 0.5)
print con_conts
database = generate_database(G, sensors, con_conts)
generate_database_in_csv(database, 'database.csv')

direct_time = []
csv_time = []

for l in range (0, 10):
	sensor_readings = generate_dict(sensors)
	C_c = generate_dict(con_conts)
	# time used by directly getting compatible states
	start = time.time()
	states1 = compatible_states(G, sensor_readings, C_c)
	end = time.time()
	direct_time.append(end - start)
	# time used by reading from database
	start = time.time()
	states2 = get_compatible_states_from_database('database.csv', sensor_readings, C_c)
	end = time.time()
	csv_time.append(end - start)
	# verification
	verifier(states1, states2)

average_time_1 = sum(direct_time)/len(direct_time)
average_time_2 = sum(csv_time)/len(csv_time)
print 'number of components: '
print '--ratio between sensor and components: '
print '----ratio of controllable contactors: '
print '------direct: ' + str(average_time_1)
print '------read: ' + str(average_time_2)
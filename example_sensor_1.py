import networkx as nx
from specs import *
import time

filename = 'circuit_sensor_1.net'
G = nx.DiGraph()
G = read_netlist(filename)
uncon_comp_tups = []
contactor_tups = []
declaration = init(G, uncon_comp_tups, contactor_tups)

# example of getting the measurement
states = {'G1': 0, 'G2': 0, 'T1': 1, 'T2': 1, 'C1': 0, 'C2': 1, 'C3': 1, 'C4': 1, 'C5': 1, 'C6': 1}
sensor = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)

# example of finding the compatible states
C_c = {'C1': 0, 'C3': 0, 'C4': 0, 'C6': 0}
S_readings = {'S1': 1, 'S2': 0}
compatible_states(G, S_readings, C_c)

# example of generating the database
sensors = ['S1', 'S2'] #sensors
con_conts = ['C1', 'C3', 'C4', 'C6'] #controllable contactors
result1 = generate_database(G, sensors, con_conts)
generate_database_in_csv(result1, 'database.csv')
result2 = get_compatible_states_from_database('database.csv', sensors, con_conts)

# test time
start1 = time.time()
t1 = generate_database(G, sensors, con_conts)
end1 = time.time()
print end1 - start1

start2 = time.time()
t2 = get_compatible_states_from_database('database.csv', sensors, con_conts)
end2 = time.time()
print end2 - start2

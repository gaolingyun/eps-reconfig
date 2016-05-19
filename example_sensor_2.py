import networkx as nx
from specs import *
import time

filename = 'circuit_sensor_2.net'
G = nx.DiGraph()
G = read_netlist(filename)
uncon_comp_tups = []
contactor_tups = []
declaration = init(G, uncon_comp_tups, contactor_tups)

# define the states
states = {'G1': 0, 'G2': 1, 'G3': 1, 'T1': 1, 'T2': 1, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 0, 'C5': 1, 'C6': 0, 'C7': 1, 'C8': 1}
# get the measurement
sensor = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)

# example of finding the compatible states
C_c = {'C1': 1, 'C2': 0, 'C3': 0, 'C4': 1, 'C5': 0, 'C7': 0, 'C8': 1}
S_readings = {'S1': 1, 'S2': 0, 'S3': 1}
compatible_states(G, S_readings, C_c)

# test time
sensors = ['S1', 'S2', 'S3']
con_conts = ['C1', 'C3', 'C4', 'C6']

start1 = time.time()
t1 = generate_database(G, sensors, con_conts)
end1 = time.time()
print end1 - start1

generate_database_in_csv(t1, 'database.csv')

start2 = time.time()
t2 = get_compatible_states_from_database('database.csv', sensors, con_conts)
end2 = time.time()
print end2 - start2
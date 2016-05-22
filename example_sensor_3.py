import networkx as nx
from specs import *
import time

filename = 'circuit_sensor_3.net'
G = nx.DiGraph()
G = read_netlist(filename)
uncon_comp_tups = []
contactor_tups = []
declaration = init(G, uncon_comp_tups, contactor_tups)

# define the states
states = {'G1': 0, 'G2': 1, 'G3': 0, 'G4': 0, 'T1': 1, 'T2': 1, 'C1': 1, 'C2': 0, 'C3': 0, 'C4': 1, 'C5': 0, 'C6': 0, 'C7': 1, 'C8': 1, 'C9': 1, 'C10': 1}
# get the measurement
sensor = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)

# example of finding the compatible states
C_c = {'C1': 1, 'C3': 1, 'C10': 0, 'C9': 1, 'C4': 0, 'C6': 1, 'C8': 0, 'C5': 1}
S_readings = {'S1': 0, 'S2': 1, 'S3': 0, 'S4': 1}
compatible_list = compatible_states(G, S_readings, C_c)

# generate database
sensors = ['S1', 'S2', 'S3', 'S4']
con_conts = ['C1', 'C3', 'C4', 'C6', 'C2', 'C9']
result = generate_database(G, sensors, con_conts)
generate_database_in_csv(result, 'database3.csv')

start1 = time.time()
compatible_states(G, S_readings, C_c)
end1 = time.time()
print end1 - start1

start2 = time.time()
get_compatible_states_from_database('database3.csv', S_readings, C_c)
end2 = time.time()
print end2 - start2

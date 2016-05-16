import networkx as nx
from specs import *

filename = 'circuit_sensor_1.net'
G = nx.DiGraph()
G = read_netlist(filename)
uncon_comp_tups = []
contactor_tups = []
declaration = init(G, uncon_comp_tups, contactor_tups)

# define the states
states = {'G1': 0, 'G2': 0, 'T1': 1, 'T2': 1, 'C1': 0, 'C2': 1, 'C3': 1, 'C4': 1, 'C5': 1, 'C6': 1}
# get the measurement
sensor = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)
print sensor

# example of finding the compatible states
C_c = {'C1': 1, 'C2': 1, 'C3': 1, 'C4': 1, 'C5': 1}
S_readings = {'S1': 0, 'S2': 0}
compatible_states(G, S_readings, C_c, '0.csv')
S_readings = {'S1': 0, 'S2': 1}
compatible_states(G, S_readings, C_c, '1.csv')
S_readings = {'S1': 1, 'S2': 0}
compatible_states(G, S_readings, C_c, '2.csv')
S_readings = {'S1': 1, 'S2': 1}
compatible_states(G, S_readings, C_c, '3.csv')
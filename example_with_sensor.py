import networkx as nx
from specs import *

filename = 'simple_circuit_with_sensor.net'
resultfile = 'example_with_sensor.txt'
G = nx.DiGraph()
G = read_netlist(filename)
uncon_comp_tups = []
contactor_tups = []
declaration = init(G, uncon_comp_tups, contactor_tups)

# define the states
states = {'G1': 1, 'G2': 0, 'T1': 0, 'T2': 0, 'C1': 1, 'C2': 1, 'C3': 1, 'C4': 0, 'C5': 0, 'C6': 0}
# get the measurement
sensor = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)
print sensor
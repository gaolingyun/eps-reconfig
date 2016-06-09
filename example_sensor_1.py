from greedy import *
import time

filename = 'circuit_sensor_1.net'
G = nx.DiGraph()
G = read_netlist(filename)
uncon_comp_tups = []
contactor_tups = []
declaration = init(G, uncon_comp_tups, contactor_tups)

'''
# example of getting the measurement
states = {'G1': 0, 'G2': 0, 'T1': 1, 'T2': 1, 'C1': 0, 'C2': 1, 'C3': 1, 'C4': 1, 'C5': 1, 'C6': 1}
sensor = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)

# example of finding the compatible states
C_c = {'C1': 0, 'C3': 0, 'C4': 1, 'C6': 1}
S_readings = {'S1': 1, 'S2': 0}
print compatible_states(G, S_readings, C_c)
'''

# generating the database
sensors = ['S1', 'S2'] #sensors
con_conts = ['C1', 'C3', 'C4', 'C6'] #controllable contactors
result = generate_database(G, sensors, con_conts, 'database1.csv')

# test the greedy strategy
actual_state = {'G2': 1, 'G1': 1, 'T2': 0, 'T1': 0, 'C2': 0, 'C5': 1}
initial_action = {'C1': 1, 'C3': 1, 'C4': 1, 'C6': 1}
states = actual_state.copy()
states.update(initial_action)
initial_reading = sensor_measurement(G, uncon_comp_tups, contactor_tups, states)
print find_state(G, actual_state, initial_action, initial_reading, 'database1.csv')

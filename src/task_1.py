import os
import sys

from scheduler.fcfs_scheduler import FirstComeFirstServedScheduler

from scheduler.simulate import parse_process_info_data, simulate_from_process_info

if not (2 <= len(sys.argv) <= 4):
    print("Expected at 1 to 4 arguments - At least the path of the simulated processes information.")
    quit()
directory = sys.argv[1]
is_debug = False
is_immediate = False
for a in range(2, len(sys.argv)):
    argument = sys.argv[a]
    if argument == "-d":
        is_debug = True
    elif argument == "-i":
        is_immediate = True
if not os.path.isfile(directory):
    print("{} was an invalid file path.".format(directory))
    quit()
with open(directory) as fs:
    process_data_lines = fs.readlines()
    process_data = parse_process_info_data(process_data_lines)
    simulate_from_process_info(process_data, FirstComeFirstServedScheduler(), is_immediate, is_debug)

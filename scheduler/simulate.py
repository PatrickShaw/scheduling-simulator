from time import sleep
from typing import List

from scheduler.fcfs_scheduler import FirstComeFirstServedScheduler
from scheduler.round_robin_scheduler import RoundRobinScheduler
from scheduler.srt_scheduler import ShortestRemainingTimeScheduler

from scheduler.scheduler import Scheduler
from scheduler.process import Process
from scheduler.process import ProcessInfo


class SimulationProcessingInformation:
    """
    That needs to be collected by the simulation goes in here
    """

    def __init__(self, total_process_count):
        self.average_turnover_time = 0
        self.average_waiting_time = 0
        self.finished_process_count = 0
        """The number of processes that have finished so far"""
        self.total_process_count = total_process_count
        """The number of processes to be processed"""


def create_simulation_processes(process_info_data: List[ProcessInfo]) -> List[Process]:
    """
    Creates a list of simulated processes, for use in a scheduler simulation.
        :param process_info_data:
            A list of process information to be used for the creation of the process. A single process will be created per
            item.
        :return:
            A list of simulated processes, ordered by their arrival time, starting from the earliest arrival to the latest
            arrival
    """
    processes = []
    for i in range(len(process_info_data)):
        processes.append(Process(process_info_data[i]))
    processes.sort(key=lambda p: p.process_info.arrival_time)
    return processes


def simulate_from_process_info(
        process_info_data: List[ProcessInfo],
        scheduler: Scheduler,
        immediately_output_information: bool = False,
        is_debug_output_enabled: bool = False):
    """
    Begins a simulation of processes arriving, being enqueued and then executed.
        :param process_info_data:
            The data being processed by the
        :param scheduler:
            The type of scheduler to be used in the simulation
        :param immediately_output_information:
            Whether to wait immediately output processing information or to wait for as many seconds as each process
            runs for.
        :param is_debug_output_enabled:
            Whether to print out debugging information such as how long and which processes are being executed.
    """
    processes = create_simulation_processes(process_info_data)
    simulate(processes, scheduler, immediately_output_information, is_debug_output_enabled)


def bind_debugging_output(processes: List[Process] = list(), scheduler: Scheduler = None):
    """
    Binds debugging listeners to a scheduler simulation for legible debugging.
        :param processes:
            The processes being bound.
        :param scheduler:
            The scheduler being bound
    """
    output_process_finished_listener = (
        lambda finished_process:
        print(str(finished_process) + " finished")
    )
    output_process_executed_listener = (
        lambda executed_process, allocated_time, execution_time:
        print("{} is executed for: {}".format(str(executed_process), execution_time))
    )
    if processes is not None:
        for process in processes:
            process.register_on_finished_listener(output_process_finished_listener)
            process.register_on_executed_listener(output_process_executed_listener)
    if scheduler is not None:
        scheduler.register_on_process_enqueuing_listener(
            lambda enqueued_process:
            print("{} was enqueued".format(enqueued_process.process_info.pid))
        )


def on_process_finished(
        finished_process: Process,
        scheduler: Scheduler,
        simulation_info: SimulationProcessingInformation):
    """
    A method used to collect and output information about a process being finished
        :param finished_process:
            The process that finished
        :param scheduler:
            The scheduler used to process the process
        :param simulation_info:
            The object used to store the information being recorded about the simulation
    """
    simulation_info.finished_process_count += 1
    simulation_info.average_turnover_time += finished_process.turnaround_time
    simulation_info.average_waiting_time += finished_process.waiting_time
    print("PID: \t\t\t\t\t\t{}".format(finished_process.pid))
    print("Turnaround time: \t\t\t{} seconds".format(finished_process.turnaround_time))
    print("Waiting time: \t\t\t\t{} seconds".format(finished_process.waiting_time))
    print()
    if simulation_info.total_process_count <= simulation_info.finished_process_count:
        simulation_info.average_waiting_time /= simulation_info.total_process_count
        simulation_info.average_turnover_time /= simulation_info.total_process_count
        throughput = simulation_info.total_process_count / scheduler.time_elapsed
        print("Average turnaround time: \t{} seconds".format(simulation_info.average_turnover_time))
        print("Average waiting time: \t\t{} seconds".format(simulation_info.average_waiting_time))
        print("Throughput: \t\t\t\t{} processes per second".format(throughput))


def simulate(
        processes: List[Process],
        scheduler: Scheduler,
        immediately_output_information: bool = False,
        is_debug_output_enabled: bool = False):
    """
    Begins a simulation of processes arriving, being enqueued and then executed.
        :param processes:
            The processes used in the simulation
        :param scheduler:
            The type of scheduler to be used in the simulation
        :param immediately_output_information:
            Whether to wait immediately output processing information or to wait for as many seconds as each process
            runs for.
        :param is_debug_output_enabled:
            Whether to print out debugging information such as how long and which processes are being executed.
    """
    if not immediately_output_information:
        for process in processes:
            process.register_on_executed_listener(
                lambda executed_process, allocated_time, executed_time:
                sleep(executed_time)
            )
    if is_debug_output_enabled:
        bind_debugging_output(processes, scheduler)
    simulation_info = SimulationProcessingInformation(len(processes))
    for process in processes:
        process.register_on_finished_listener(
            lambda finished_process:
            on_process_finished(finished_process, scheduler, simulation_info)
        )
    for process in processes:
        time_till_process_arrives = max(0, process.process_info.arrival_time - scheduler.time_elapsed)
        scheduler.increase_time(time_till_process_arrives)
        scheduler.enqueue_process(process)
    scheduler.finish()


def parse_process_info(process_info_string: str) -> ProcessInfo:
    """
    Parses a string and creates process information to be used in a scheduler simulation.
        :param process_info_string:
            The string being parsed.
            Should be of the format "<PID>, <arrival-time>, <processing-time>
        :return:
            The parsed process information.
    """
    split_process_info_string = process_info_string.split()
    pid = split_process_info_string[0]
    arrival_time = int(split_process_info_string[1])
    total_processing_time = int(split_process_info_string[2])
    return ProcessInfo(pid, arrival_time, total_processing_time)


def parse_process_info_data(process_info_lines: List[str]) -> List[ProcessInfo]:
    """
    Parses a series of lines and creates a single item of process information per line.
    :param process_info_lines:
        The strings being parsed.
    :return:
        The parse process information data.
    """
    process_information_data = []
    for line in process_info_lines:
        process_information_data.append(parse_process_info(line))
    return process_information_data
"""
    Below are examples simulations of all examples in lecture 9 of FIT2070.
"""
if __name__ == "__main__":
    example_process_information = [
            ProcessInfo("A", 0, 3),
            ProcessInfo("B", 2, 6),
            ProcessInfo("C", 4, 4),
            ProcessInfo("D", 6, 5),
            ProcessInfo("E", 8, 2),
        ]
    print("First come first served")
    simulate_from_process_info(
        example_process_information,
        FirstComeFirstServedScheduler(),
        True,
        True
    )
    print()

    print("Round robin q = 1")
    simulate_from_process_info(
        example_process_information,
        RoundRobinScheduler(1),
        True,
        True
    )
    print()

    print("Round robin q = 4 ")
    simulate_from_process_info(
        example_process_information,
        RoundRobinScheduler(4),
        True,
        True
    )
    print()

    print("Shortest remaining time scheduler")
    simulate_from_process_info(
        example_process_information,
        ShortestRemainingTimeScheduler(),
        True,
        True
    )

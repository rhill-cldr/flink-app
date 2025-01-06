from typing import List, Tuple
from dataclasses import dataclass
from decimal import Decimal, getcontext
from ortools.linear_solver import pywraplp

# Decimal precision
getcontext().prec = 2

NUM_FLINK_JOBS = 100
NUM_TASKS = [2,2,2,2,2,3,3,5,5,10] * (NUM_FLINK_JOBS // 10)

@dataclass
class FlinkJob:
    """Flink Job Details"""
    name: str
    tasks: int

@dataclass
class FlinkService:
    """Flink Service Configuration"""
    taskmanager_number_of_task_slots: int
    parallelism_default: int
    taskmanager_managed_memory_fraction: Decimal
    taskmanager_memory_process_size: int  # GiB
    jobmanager_heap_size: int  # GiB
    taskmanager_network_memory_max: int # GiB
    taskmanager_network_memory_fraction: Decimal

def estimate_cluster_sizing(jobs: List[FlinkJob], flink_service: FlinkService) -> Tuple[int, int]:
    """
    Estimate the required memory and vcores for a CDP cluster based on the given Flink jobs.

    :param jobs: List of Flink jobs with known numbers of tasks.
    :param flink_service: Flink service configuration.
    :return: Tuple of required memory (in GiB) and vcores.
    """
    total_tasks = sum(job.tasks * flink_service.parallelism_default for job in jobs)
    total_taskmanagers = (total_tasks + flink_service.taskmanager_number_of_task_slots - 1) // flink_service.taskmanager_number_of_task_slots

    # Calculate memory per TaskManager
    taskmanager_memory_process_size = flink_service.taskmanager_memory_process_size
    taskmanager_network_memory = flink_service.taskmanager_network_memory_max
    taskmanager_managed_memory_fraction = flink_service.taskmanager_managed_memory_fraction

    # Calculate managed memory per TaskManager
    taskmanager_managed_memory = taskmanager_memory_process_size * taskmanager_managed_memory_fraction

    # Calculate total memory per TaskManager
    total_memory_per_taskmanager = taskmanager_memory_process_size + taskmanager_network_memory + taskmanager_managed_memory

    required_memory = total_taskmanagers * total_memory_per_taskmanager
    required_vcores = total_taskmanagers * flink_service.taskmanager_number_of_task_slots

    return required_memory, required_vcores



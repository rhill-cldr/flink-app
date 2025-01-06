from typing import List, Tuple
from dataclasses import dataclass
from decimal import Decimal, getcontext


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


@dataclass
class FlinkConf:
    """   """
    service: FlinkService


@dataclass
class YarnQueue:
    """Yarn Queue Details"""
    name: str
    min_user_limit: int  # percent
    user_limit_factor: Decimal


@dataclass
class YarnService:
    """Yarn Service Configuration"""
    yarn_nodemanager_resource_memory: int  # GiB
    yarn_nodemanager_resource_cpu_vcores: int


@dataclass
class YarnConf:
    pass


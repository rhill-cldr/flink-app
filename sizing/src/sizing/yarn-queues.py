from dataclasses import dataclass
from decimal import Decimal, getcontext
from ortools.linear_solver import pywraplp

#
# |Variable|Label|Description|
# |---|---|---|
# |task_manager_number_of_task_slots|TaskManager Number of Task Slots| |
# |parallelism_default|Default Parallelism|Default parallelism for jobs|
# |yarn_nodemanger_resource_memory|Container Memory|Amount of memory, in MiB, that can be allocated for containers|
# |yarn_nodemanager_resource_cpu_vcores|Container Virtual CPU Cores|Number of virtual CPU cores that can be allocated for containers|
#

# Number of YARN queues available for Flink jobs.
# Assume jobs and containers will be evenly allocated.
NUM_YARN_QUEUES = 3

# Assume tasks per job may range from 1 to 10
NUM_FLINK_JOBS = 30
NUM_TASKS = [1, 2, 2, 2, 4, 4, 4, 8, 8, 10] * 3

assert(NUM_FLINK_JOBS == len(NUM_TASKS))

# Decimal precision
getcontext().prec = 2


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
    # Parameters not needed for this implementation
    #yarn_application_attempts: int
    #yarn_containerized_heap_cutoff_ratio: float
    #yarn_containerized_heap_cutoff_relative_threshold: float
    #yarn_resourcemanager_scheduler_capacity_root_default_capacity: int
    #yarn_resourcemanager_scheduler_capacity_root_default_maximum_capacity: int


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
    taskmanager_memory_process_size: int # GiB
    jobmanager_heap_size: int # GiB
    taskmanager_network_memory_fraction: Decimal
    

@dataclass
class OptimizationResult:
    """Results of Mixed-Integer Optimization"""
    pass


def _create_yarn_queues(num_queues: int):
    for i in range(num_queues):
        yield YarnQueue(f"Queue {i}", 10, Decimal("1.0"))


def perform_optmization(queues, yarn_service: YarnService, flink_service: FlinkService) -> OptimizationResult:
    """Optimization Implementation using bin-packing logic"""
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        raise Exception("Solver not created")

    # Create data model
    data = {}
    data["jobs"] = [FlinkJob(f"Job {i}", tasks=NUM_TASKS[i]) for i in range(NUM_FLINK_JOBS)]
    data["items"] = list(range(len(data["jobs"])))
    data["bins"] = list(range(len(queues)))
    data["bin_capacities"] = [yarn_service.yarn_nodemanager_resource_memory] * len(queues)
    data["weights"] = [job.tasks for job in data["jobs"]]

    # Variables
    # x[i, j] = 1 if job i is packed in queue j.
    x = {}
    for i in data["items"]:
        for j in data["bins"]:
            x[(i, j)] = solver.IntVar(0, 1, "x_%i_%i" % (i, j))

    # y[j] = 1 if queue j is used.
    y = {}
    for j in data["bins"]:
        y[j] = solver.IntVar(0, 1, "y[%i]" % j)

    # Constraints
    # Each job must be in exactly one queue.
    for i in data["items"]:
        solver.Add(sum(x[i, j] for j in data["bins"]) == 1)

    # The amount packed in each queue cannot exceed its capacity.
    for j in data["bins"]:
        solver.Add(
            sum(x[(i, j)] * data["weights"][i] for i in data["items"])
            <= y[j] * data["bin_capacities"][j]
        )

    # Objective: minimize the number of queues used.
    solver.Minimize(solver.Sum([y[j] for j in data["bins"]]))

    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    result = OptimizationResult()
    if status == pywraplp.Solver.OPTIMAL:
        num_queues_used = 0
        for j in data["bins"]:
            if y[j].solution_value() == 1:
                queue_jobs = []
                queue_weight = 0
                for i in data["items"]:
                    if x[i, j].solution_value() > 0:
                        queue_jobs.append(data["jobs"][i].name)
                        queue_weight += data["weights"][i]
                if queue_jobs:
                    num_queues_used += 1
                    print("Queue number", j)
                    print("  Jobs packed:", queue_jobs)
                    print("  Total weight:", queue_weight)
                    print()
        print()
        print("Number of queues used:", num_queues_used)
        print("Time = ", solver.WallTime(), " milliseconds")
        result.num_queues_used = num_queues_used
    else:
        print("The problem does not have an optimal solution.")
        result.num_queues_used = len(data["bins"])

    return result


def main():
    yarn_service = YarnService(
        yarn_nodemanager_resource_memory=58,
        yarn_nodemanager_resource_cpu_vcores=64,
    )
    
    flink_service = FlinkService(
        taskmanager_number_of_task_slots=4,
        parallelism_default=8,
        taskmanager_memory_process_size=2,
        jobmanager_heap_size=1,
        taskmanager_network_memory_fraction=Decimal(0.1)
    )
    
    queues = [q for q in _create_yarn_queues(NUM_YARN_QUEUES)]
    # perform optimization
    result = perform_optmization(queues, yarn_service, flink_service)
    print(result)


if __name__ == "__main__":
    main()


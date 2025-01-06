

| Variable | Label | Default | Description |
|---|---|---|---|
| taskmanager_memory_process_size | TaskManager Process Memory Size | 2 GiB | This includes all the memory that a TaskExecutor consumes, consisting of Total Flink Memory, JVM Metaspace, and JVM Overhead. On containerized setups, this should be set to the container memory. See also 'taskmanager.memory.flink.size' for total Flink memory size configuration. |
| taskmanager_managed_memory_fraction | TaskManager Managed Memory Fraction | 0.4 | Fraction of Total Flink Memory to be used as Managed Memory, if Managed Memory size is not explicitly specified. Managed memory is used by Flink operators (caching, sorting, hashtables) and state backends (RocksDB). |
| taskmanager_network_memory_max | Network Buffer Memory Max | 2 GiB | Max Network Memory size for TaskExecutors. Network Memory is off-heap memory reserved for ShuffleEnvironment (e.g., network buffers). Network Memory size is derived to make up the configured fraction of the Total Flink Memory. If the derived size is less/greater than the configured min/max size, the min/max size will be used. The exact size of Network Memory can be explicitly specified by setting the min/max to the same value. |
| taskmanager_network_memory_fraction  | Network Buffer JVM Memory Fraction | 0.1 | Fraction of JVM memory to use for network buffers. This determines how many streaming data exchange channels a TaskManager can have at the same time and how well buffered the channels are. If a job is rejected or you get a warning that the system has not enough buffers available, increase this value or the min/max values below. Also note, that 'taskmanager.memory.network.min' and 'taskmanager.memory.network.max' may override this fraction. |

## Updates to flink-yarn.py

- **Added Configuration Options for YarnService:**
  - `yarn_nodemanager_resource_memory`: Container Memory. Amount of memory, in GiB, that can be allocated for containers.
  - `yarn_nodemanager_resource_cpu_vcores`: Container Virtual CPU Cores. Number of virtual CPU cores that can be allocated for containers.
- **Parameters not needed for this implementation:**
  - `yarn_application_attempts`: Number of application attempts.
  - `yarn_containerized_heap_cutoff_ratio`: Heap cutoff ratio for containers.
  - `yarn_containerized_heap_cutoff_relative_threshold`: Relative threshold for heap cutoff.
  - `yarn_resourcemanager_scheduler_capacity_root_default_capacity`: Capacity of the default queue.
  - `yarn_resourcemanager_scheduler_capacity_root_default_maximum_capacity`: Maximum capacity of the default queue.

- **Added Configuration Options for FlinkService:**
  - `jobmanager_heap_size`: Memory allocated for the JobManager.

- **Updated perform_optmiization Function:**
  - The function now takes `yarn_service` and `flink_service` as parameters and uses these configurations for optimization.

- **Updated main Function:**
  - The main function now initializes `yarn_service` and `flink_service` with the new configuration options and passes them to the `perform_optmiization` function.

## Calculation Methodology

The cluster sizing calculation is based on the following formulas and considerations:

### TaskManager Memory Calculation

The total memory required for each TaskManager is calculated using the following formula:

$$ \text{TaskManager Memory} = \text{taskmanager\_memory\_process\_size} $$

This includes all the memory that a TaskExecutor consumes, consisting of Total Flink Memory, JVM Metaspace, and JVM Overhead.

### Managed Memory Calculation

Managed memory is a fraction of the Total Flink Memory and is calculated as:

$$ \text{Managed Memory} = \text{taskmanager\_memory\_process\_size} \times \text{taskmanager\_managed\_memory\_fraction} $$

Managed memory is used by Flink operators (caching, sorting, hashtables) and state backends (RocksDB).

### Network Memory Calculation

Network memory is off-heap memory reserved for ShuffleEnvironment (e.g., network buffers) and is calculated as:

$$ \text{Network Memory} = \text{taskmanager\_memory\_process\_size} \times \text{taskmanager\_network\_memory\_fraction} $$

If the derived size is less than the configured minimum or greater than the configured maximum, the minimum or maximum size will be used.

### Total Memory and vCores Calculation

The total memory and vCores required for the cluster are calculated based on the number of tasks and the configuration parameters provided. The total memory is the sum of the memory required for all TaskManagers, and the total vCores are the sum of the vCores required for all TaskManagers.

$$ \text{Total Memory} = \text{Number of TaskManagers} \times \text{TaskManager Memory} $$

$$ \text{Total vCores} = \text{Number of TaskManagers} \times \text{taskmanager\_number\_of\_task\_slots} $$

The number of TaskManagers is determined based on the total number of tasks and the number of slots per TaskManager.

$$ \text{Number of TaskManagers} = \lceil \frac{\text{Total Tasks}}{\text{taskmanager\_number\_of\_task\_slots}} \rceil $$

These calculations ensure that the cluster is appropriately sized to handle the given set of Flink jobs.



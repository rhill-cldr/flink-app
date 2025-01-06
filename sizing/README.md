
# Platform Configurations

**note** Default values are taken from a reference cluster. Some resource allocation configuration options are omitted from this table, and not that are present are used in the simplified estimation.


| Service | Variable | Label | Default | Description |
|---|---|---|---|---|
| Flink | parallelism_default | Default Parallelism | 1 | Default parallelism for jobs |
| Flink | jobmanager_heap_size | JobManager Heap Size | 1 GB | JVM heap size for the JobManager |
| Flink | taskmanager_memory_process_size | TaskManager Process Memory Size | 2 GB | This includes all the memory that a TaskExecutor consumes, consisting of Total Flink Memory, JVM Metaspace, and JVM Overhead. On containerized setups, this should be set to the container memory. See also 'taskmanager.memory.flink.size' for total Flink memory size configuration. |
| Flink | taskmanager_managed_memory_fraction | TaskManager Managed Memory Fraction | 0.4 | Fraction of Total Flink Memory to be used as Managed Memory, if Managed Memory size is not explicitly specified. Managed memory is used by Flink operators (caching, sorting, hashtables) and state backends (RocksDB). |
| Flink | taskmanager_number_of_task_slots | TaskManager Number of Task Slots| 1 | The number of parallel operator or user function instances that a single TaskManager can run. If this value is larger than 1, a single TaskManager takes multiple instances of a function or operator. That way, the TaskManager can utilize multiple CPU cores, but at the same time, the available memory is divided between the different operator or function instances. This value is typically proportional to the number of physical CPU cores that the TaskManager's machine has (e.g., equal to the number of cores, or half the number of cores). |
| Flink | taskmanager_network_memory_fraction  | Network Buffer JVM Memory Fraction | 0.1 | Fraction of JVM memory to use for network buffers. This determines how many streaming data exchange channels a TaskManager can have at the same time and how well buffered the channels are. If a job is rejected or you get a warning that the system has not enough buffers available, increase this value or the min/max values below. Also note, that 'taskmanager.memory.network.min' and 'taskmanager.memory.network.max' may override this fraction. |
| Flink | taskmanager_network_memory_max | Network Buffer Memory Max | 2 GB | Max Network Memory size for TaskExecutors. Network Memory is off-heap memory reserved for ShuffleEnvironment (e.g., network buffers). Network Memory size is derived to make up the configured fraction of the Total Flink Memory. If the derived size is less/greater than the configured min/max size, the min/max size will be used. The exact size of Network Memory can be explicitly specified by setting the min/max to the same value. |
| YARN | yarn_nodemanager_container_manager_thread_count | Container Manager Thread Count (per-group) | 20 | Number of threads container manager uses. |
| YARN | yarn_nodemanager_delete_thread_count | Cleanup Thread Count | 4 | Number of threads used in cleanup. |
| YARN | yarn_nodemanager_localizer_client_thread_count | Localizer Client Thread Count | 5 | Number of threads to handle localization requests. |
| YARN | yarn_nodemanager_localizer_fetch_thread_count | Localizer Fetch Thread Count | 4 | Number of threads to use for localization fetching. |
| YARN | yarn_resourcemanager_client_thread_count | Client Thread Count | 50 | The number of threads used to handle applications manager requests. |
| YARN | yarn_resourcemanager_scheduler_client_thread_count | Scheduler Thread Count | 50 | The number of threads used to handle requests through the scheduler interface. |
| YARN | yarn_nodemanager_resource_memory_mb | Container Memory (Per NM Group) | 58.36 GB | Amount of physical memory, in MB, that can be allocated for containers. |
| YARN | yarn_nodemanager_resource_cpu_vcores | Container Virtual CPU Cores| 64 | Number of virtual CPU cores that can be allocated for containers |
| YARN | resource_manager_java_heapsize | Java Heap Size of ResourceManager in Bytes | 1 GB | Maximum size in bytes for the Java Process heap memory. Passed to Java -Xmx. |
| YARN | yarn_scheduler_minimum_allocation_mb | Container Memory Minimum | 1 GB | The smallest amount of physical memory, in MB, that can be requested for a container. If using the Capacity or FIFO scheduler, memory requests will be rounded up to the nearest multiple of this number. |
| YARN | yarn_scheduler_increment_allocation_mb | Container Memory Increment | 512 MB | If using the Fair Scheduler, memory requests will be rounded up to the nearest multiple of this number. |
| YARN | yarn_scheduler_maximum_allocation_mb | Container Memory Maximum | 69.37 GB | The largest amount of physical memory, in MiB, that can be requested for a container. |
| YARN | node_manager_java_heapsize | Java Heap Size of NodeManager in Bytes | 1 GB | Maximum size in bytes for the Java Process heap memory. Passed to Java -Xmx. |
| YARN | yarn_scheduler_minimum_allocation_vcores | Container Virtual CPU Cores Minimum | 1 | The smallest number of virtual CPU cores that can be requested for a container. If using the Capacity or FIFO scheduler, virtual core requests will be rounded up to the nearest multiple of this number. |
| YARN | yarn_scheduler_increment_allocation_vcores | Container Virtual CPU Cores Increment | 1 | If using the Fair Scheduler, virtual core requests will be rounded up to the nearest multiple of this number. |
| YARN | yarn_scheduler_maximum_allocation_vcores | Container Virtual CPU Cores Maximum | 64 | The largest number of virtual CPU cores that can be requested for a container. |


- **Parameters not needed for this implementation:**
  - `yarn_application_attempts`: Number of application attempts.
  - `yarn_containerized_heap_cutoff_ratio`: Heap cutoff ratio for containers.
  - `yarn_containerized_heap_cutoff_relative_threshold`: Relative threshold for heap cutoff.
  - `yarn_resourcemanager_scheduler_capacity_root_default_capacity`: Capacity of the default queue.
  - `yarn_resourcemanager_scheduler_capacity_root_default_maximum_capacity`: Maximum capacity of the default queue.

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



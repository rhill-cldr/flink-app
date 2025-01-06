import math
 from dataclasses import dataclass
 from typing import List, Dict, Optional
 from ortools.linear_solver import pywraplp
 from ortools.sat.python import cp_model
 
 @dataclass
 class ClouderaFlinkJob:
     name: str
     parallelism: int
     state_backend: str  # 'memory' or 'rocksdb'
     state_size_gb: float
     checkpoint_interval_sec: int
     avg_throughput_records_sec: int
     peak_throughput_records_sec: int
     input_record_size_kb: float
     output_record_size_kb: float
     priority: int = 1  # 1-5, higher number means higher priority
     # Cloudera-specific parameters
     security_enabled: bool = True  # Kerberos authentication
     ha_enabled: bool = True       # High availability
     tls_enabled: bool = True      # TLS encryption
     log_level: str = "INFO"
     target_latency_ms: int = 1000
 
 class ClouderaFlinkOptimizer:
     def __init__(
         self,
         node_memory_gb: float,
         node_vcores: int,
         nodes_in_cluster: int,
         cdh_version: str,          # e.g., "7.1.7"
         parcel_directory: str = "/opt/cloudera/parcels",
         os_reserved_memory_gb: float = 4,
         yarn_reserved_memory_gb: float = 2,
         redundancy_factor: float = 1.2,
         # Cloudera-specific parameters
         cgroup_enabled: bool = True,
         rack_awareness_enabled: bool = True,
         knox_enabled: bool = True,
         ranger_enabled: bool = True,
         atlas_enabled: bool = True
     ):
         self.node_memory_gb = node_memory_gb
         self.node_vcores = node_vcores
         self.nodes_in_cluster = nodes_in_cluster
         self.cdh_version = cdh_version
         self.parcel_directory = parcel_directory
         self.os_reserved_memory_gb = os_reserved_memory_gb
         self.yarn_reserved_memory_gb = yarn_reserved_memory_gb
         self.redundancy_factor = redundancy_factor
         
         # Cloudera-specific settings
         self.cgroup_enabled = cgroup_enabled
         self.rack_awareness_enabled = rack_awareness_enabled
         self.knox_enabled = knox_enabled
         self.ranger_enabled = ranger_enabled
         self.atlas_enabled = atlas_enabled
         
         # Cloudera-specific memory adjustments
         self.cloudera_overhead = self._calculate_cloudera_overhead()
     
     def _calculate_cloudera_overhead(self) -> Dict:
         """Calculate Cloudera-specific overhead based on enabled features."""
         overhead = {
             "memory_gb": 0,
             "cpu_percentage": 0
         }
         
         # Kerberos and security overhead
         if self.ranger_enabled:
             overhead["memory_gb"] += 0.5  # Ranger policy enforcement
             overhead["cpu_percentage"] += 2
             
         if self.atlas_enabled:
             overhead["memory_gb"] += 0.3  # Atlas metadata tracking
             overhead["cpu_percentage"] += 1
             
         if self.knox_enabled:
             overhead["memory_gb"] += 0.2  # Knox gateway
             overhead["cpu_percentage"] += 1
         
         # CGroups overhead
         if self.cgroup_enabled:
             overhead["memory_gb"] += 0.1
             overhead["cpu_percentage"] += 1
         
         return overhead
 
     def _get_cdh_specific_configs(self) -> Dict:
         """Get version-specific Cloudera configurations."""
         cdh_configs = {
             "7.1.7": {
                 "flink.classloader.resolver-async-timeout": "30000",
                 "yarn.scheduler.increment-allocation-mb": "512",
                 "yarn.nodemanager.runtime.linux.allowed-runtimes": "docker",
                 "container-executor.cfg.docker.allowed.networks": "host,none",
                 "container-executor.cfg.docker.privileged-containers.allowed": "false",
                 "flink.historyserver.archive.fs.dir": "/user/${user}/completed-jobs/",
                 "yarn.nodemanager.disk-health-checker.enable": "true",
                 "yarn.nodemanager.disk-health-checker.interval-ms": "120000"
             }
         }
         return cdh_configs.get(self.cdh_version, {})
 
     def _calculate_base_resources(self, job: ClouderaFlinkJob) -> Dict:
         """Calculate base resource requirements with Cloudera-specific adjustments."""
         base_resources = super()._calculate_base_resources(job)
         
         # Add Cloudera-specific memory overhead
         security_overhead_gb = 0
         if job.security_enabled:
             security_overhead_gb += 0.25  # Kerberos and encryption overhead
         
         if job.tls_enabled:
             security_overhead_gb += 0.15  # TLS overhead
             
         # High availability overhead
         ha_overhead_gb = 0.5 if job.ha_enabled else 0
         
         # Adjust memory for Cloudera monitoring and logging
         monitoring_overhead_gb = {
             "DEBUG": 0.3,
             "INFO": 0.2,
             "WARN": 0.15,
             "ERROR": 0.1
         }.get(job.log_level, 0.2)
         
         total_overhead = (
             security_overhead_gb + 
             ha_overhead_gb + 
             monitoring_overhead_gb +
             self.cloudera_overhead["memory_gb"]
         )
         
         base_resources["base_memory_gb"] += total_overhead
         
         return base_resources
 
     def generate_cloudera_specific_configs(self, job_details: Dict) -> Dict:
         """Generate Cloudera-specific configurations."""
         cdh_configs = self._get_cdh_specific_configs()
         
         # Add Cloudera security configs
         security_configs = {
             "yarn.nodemanager.container-executor.class": 
                 "org.apache.hadoop.yarn.server.nodemanager.LinuxContainerExecutor",
             "yarn.nodemanager.linux-container-executor.group": "hadoop",
             "yarn.nodemanager.linux-container-executor.resources-handler.class":
                 "org.apache.hadoop.yarn.server.nodemanager.util.CgroupsLCEResourcesHandler",
             "yarn.nodemanager.runtime.linux.docker.allowed-container-networks": "host",
             "yarn.nodemanager.runtime.linux.docker.privileged-containers.allowed": "false",
             "yarn.nodemanager.runtime.linux.docker.trusted-registries": 
                 "registry.example.com",
             "hadoop.security.credential.provider.path": 
                 "jceks://hdfs/user/flink/credentials.jceks"
         }
         
         # Add Cloudera monitoring configs
         monitoring_configs = {
             "yarn.nodemanager.health-checker.interval-ms": "135000",
             "yarn.nodemanager.health-checker.script.timeout-ms": "60000",
             "yarn.resourcemanager.nm-monitoring.enabled": "true",
             "yarn.nodemanager.recovery.enabled": "true",
             "yarn.nodemanager.recovery.dir": "/var/lib/hadoop-yarn/recovery"
         }
         
         return {
             **cdh_configs,
             **security_configs,
             **monitoring_configs,
             "cloudera.specific.recommendations": [
                 f"Configure Cloudera Manager to monitor Flink metrics",
                 f"Set up Cloudera Navigator for audit logging",
                 f"Enable Ranger policies for Flink service",
                 f"Configure Atlas for Flink metadata tracking",
                 f"Set up Knox for secure gateway access"
             ]
         }
 
     def optimize_container_allocation(self, jobs: List[ClouderaFlinkJob]) -> Dict:
         """Optimize container allocation with Cloudera-specific considerations."""
         optimization_result = super().optimize_container_allocation(jobs)
         
         if optimization_result['status'] == 'OPTIMAL':
             # Add Cloudera-specific configurations
             cloudera_configs = self.generate_cloudera_specific_configs(
                 optimization_result['job_details']
             )
             optimization_result['cloudera_configs'] = cloudera_configs
             
             # Add Cloudera-specific health checks
             optimization_result['health_checks'] = {
                 "check_parcel_directory": f"ls -l {self.parcel_directory}/CDH-{self.cdh_version}",
                 "verify_cgroups": "cat /proc/mounts | grep cgroup",
                 "check_kerberos": "klist -k /etc/hadoop/conf/hdfs.keytab",
                 "verify_knox": "curl -k https://knox.example.com:8443/gateway/cdp-proxy/",
                 "check_ranger": "ranger-admin status"
             }
         
         return optimization_result


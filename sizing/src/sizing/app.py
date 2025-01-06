import re
import json
import os
import math
from textual import on
from textual import events
from textual.app import App
from textual.containers import Grid, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, Input, Label, Select
from textual.binding import Binding
from cdp_cluster_sizing import estimate_cluster_sizing, FlinkJob, FlinkService
from server_optimizer import optimize_server_allocation
from decimal import Decimal
from jinja2 import Environment, FileSystemLoader
from zcfg import ConfigFactory
from components import NumberInput, InputGroup


class ClusterSizingApp(App):
    """A Textual app to estimate CDP cluster sizing with improved user interface."""
     
    CSS_PATH = "base.css"
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("c", "clear_inputs", "Clear", show=True),
        Binding("r", "reset_inputs", "Reset", show=True),
    ]

    _config = {}

    def __init__(self, config: ConfigFactory):
        super().__init__()
        self._config = config

    def compose(self):
        """Create child widgets for the app."""
        cnf = self._config.get("defaults.flink")
        yield Header()
        with VerticalScroll(id="container"):
            job_tasks_input_group = InputGroup("job_tasks", "Number of tasks per job (comma-separated)", ",".join(map(str,cnf.get_list("job_tasks"))))
            yield job_tasks_input_group
            cnf = self._config.get("defaults.flink.service")
            with Grid():
                yield InputGroup("task_slots", "Task Manager Slots (count)", str(cnf.get("task_slots")))
                yield InputGroup("network_memory", "Network Memory Max (MB)", str(cnf.get("network_memory")))
                yield InputGroup("memory_fraction", "Managed Memory Fraction (float)", str(cnf.get("memory_fraction")))
                yield InputGroup("parallelism", "Default Parallelism (count)", str(cnf.get("parallelism")))
                yield InputGroup("process_size", "Task Manager Memory (MB)", str(cnf.get("process_size")))
                yield InputGroup("heap_size", "Job Manager Heap Size (MB)", str(cnf.get("heap_size")))
                yield InputGroup("network_fraction", "Network Memory Fraction (float)", str(cnf.get("network_fraction")))
                
            yield Button("Calculate Sizing", variant="primary", id="calculate")
            yield Static("", id="result", classes="result")
        yield Footer()

    def action_clear_inputs(self):
        """Clear all input fields."""
        for input_widget in self.query("Input"):
            input_widget.value = ""
        self.query_one("#result").update("")

    def action_reset_inputs(self):
        """Reset all input fields to their default values."""
        cnf = self._config.get("defaults.flink")
        self.query_one("#job_tasks_input").value = ",".join(map(str,cnf.get_list("job_tasks")))
        self.query_one("#task_slots_input").value = str(cnf.get("service.task_slots"))
        self.query_one("#network_memory_input").value = str(cnf.get("service.network_memory"))
        self.query_one("#memory_fraction_input").value = str(cnf.get("service.memory_fraction"))
        self.query_one("#parallelism_input").value = str(cnf.get("service.parallelism"))
        self.query_one("#process_size_input").value = str(cnf.get("service.process_size"))
        self.query_one("#heap_size_input").value = str(cnf.get("service.heap_size"))
        self.query_one("#network_fraction_input").value = str(cnf.get("service.network_fraction"))
        self.query_one("#result").update("")

    def validate_inputs(self) -> tuple[list[FlinkJob], FlinkService, str]:
        """Validate and convert user inputs to appropriate types."""
        try:
            # Get job tasks
            jobs_input = self.query_one("#job_tasks_input").value
            jobs = [FlinkJob(f"Job {i+1}", int(task.strip())) 
                    for i, task in enumerate(jobs_input.split(","))]
            
            # Get Flink service configuration
            config = {
                'taskmanager_number_of_task_slots': int(self.query_one("#task_slots_input").value),
                'taskmanager_network_memory_max': int(self.query_one("#network_memory_input").value),
                'taskmanager_managed_memory_fraction': float(self.query_one("#memory_fraction_input").value),
                'parallelism_default': int(self.query_one("#parallelism_input").value),
                'taskmanager_memory_process_size': int(self.query_one("#process_size_input").value),
                'jobmanager_heap_size': int(self.query_one("#heap_size_input").value),
                'taskmanager_network_memory_fraction': float(self.query_one("#network_fraction_input").value)
            }
            
            flink_service = FlinkService(**config)
            
            return jobs, flink_service
            
        except ValueError as e:
            raise ValueError(f"Invalid input: Please check all fields are filled with valid numbers. {str(e)}")
 
    @on(Button.Pressed, "#calculate")
    def calculate_sizing(self):
        """Calculate and display cluster sizing based on user inputs."""
        result_widget = self.query_one("#result")
        
        try:
            jobs, flink_service = self.validate_inputs()
            required_memory, required_vcores = estimate_cluster_sizing(jobs, flink_service)
            
            # Ensure required_memory is a float
            required_memory = float(required_memory)
            
            # Load server types from equinix.json
            with open(os.path.join('library', 'equinix.json')) as f:
                server_types = json.load(f)
            
            # Assuming a default server type for calculation
            default_server_type = "c3.small.x86"
            selected_server = next((server for server in server_types if server['server_type'] == default_server_type), None)
            
            if not selected_server:
                raise ValueError(f"Default server type {default_server_type} not found in equinix.json")
            
            # Calculate the number of servers needed
            server_ram_gb = int(selected_server['hardware']['ram'].split('GB')[0])
            server_vcores = int(selected_server['hardware']['cpu_cores'])
            
            num_servers_memory = math.ceil(required_memory / server_ram_gb)
            num_servers_vcores = math.ceil(required_vcores / server_vcores)
            
            num_servers = max(num_servers_memory, num_servers_vcores)
            
            # Optimize server allocation
            redundancy_factor = 1.2  # Example redundancy factor
            optimization_result = optimize_server_allocation(required_vcores, required_memory, redundancy_factor)
            
            # Load Jinja2 environment and templates
            env = Environment(loader=FileSystemLoader('src/sizing/templates'))
            result_tmpl = env.get_template('result_text.md.j2')
            
            # Render memory text
            if required_memory < 1024:
                memory_text = "{:.2f} GiB".format(required_memory)
            else:
                memory_text = "{:.2f} TB".format(required_memory / 1024)
            
            # Render template with required_memory, required_vcores, jobs, memory_text, num_servers, and optimization_result
            result_text = result_tmpl.render(
                memory_text=memory_text,
                required_vcores=required_vcores,
                jobs=jobs,
                num_jobs=len(jobs),
                num_tasks=sum([j.tasks for j in jobs]),
                num_servers=num_servers,
                server_allocation=optimization_result.get("server_allocation", {}),
                total_cost=optimization_result.get("total_cost", 0)
            )
            result_widget.update(result_text)
            
        except Exception as e:
            result_widget.update(f"[bold red]Error:[/bold red] {str(e)}")
 
if __name__ == "__main__":
    conf = ConfigFactory.parse_file('./conf/base.conf')
    app = ClusterSizingApp(conf)
    app.run()


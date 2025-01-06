import textual
from textual.app import App
from textual.widgets import Header, Footer, Placeholder, Button
from cdp_cluster_sizing import estimate_cluster_sizing, FlinkJob, FlinkService
from decimal import Decimal

class ClusterSizingApp(App):
    """A Textual app to estimate CDP cluster sizing."""

    CSS_PATH = "cluster_sizing.css"

    def compose(self):
        yield Header()
        yield Placeholder(id="jobs")
        yield Placeholder(id="flink_service")
        yield Button(label="Estimate Cluster Sizing", id="estimate_button")
        yield Placeholder(id="result")
        yield Footer()

    def on_mount(self):
        self.query_one("#jobs").renderable = "Enter the number of tasks for each job, separated by commas:"
        self.query_one("#flink_service").renderable = "Enter Flink service configuration (taskmanager_number_of_task_slots, taskmanager_network_memory_max, taskmanager_managed_memory_fraction, parallelism_default, taskmanager_memory_process_size, jobmanager_heap_size, taskmanager_network_memory_fraction):"
        self.query_one("#result").renderable = "Result will be displayed here."
        self.query_one("#estimate_button").on_click = self.action_estimate

    def action_estimate(self):
        jobs_input = self.query_one("#jobs").renderable
        flink_service_input = self.query_one("#flink_service").renderable

        try:
            jobs = [FlinkJob(f"Job {i+1}", int(num_tasks)) for i, num_tasks in enumerate(jobs_input.split(","))]
            flink_service_values = list(map(float, flink_service_input.split(",")))
            flink_service = FlinkService(
                taskmanager_number_of_task_slots=int(flink_service_values[0]),
                taskmanager_network_memory_max=int(flink_service_values[1]),
                taskmanager_managed_memory_fraction=Decimal(str(flink_service_values[2])),
                parallelism_default=int(flink_service_values[3]),
                taskmanager_memory_process_size=int(flink_service_values[4]),
                jobmanager_heap_size=int(flink_service_values[5]),
                taskmanager_network_memory_fraction=Decimal(str(flink_service_values[6])),
            )

            required_memory, required_vcores = estimate_cluster_sizing(jobs, flink_service)
            if required_memory < 1024:
                result = f"Required Memory: {required_memory:.2f} GiB"
            else:
                required_memory_tb = required_memory / 1024
                result = f"Required Memory: {required_memory_tb:.2f} TB"
            result += f"\nRequired vCores: {required_vcores}"
        except Exception as e:
            result = f"Error: {e}"

        self.query_one("#result").update(result)

if __name__ == "__main__":
    app = ClusterSizingApp()
    app.run()


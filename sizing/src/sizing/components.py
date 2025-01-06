from textual import on
from textual import events
from textual.app import App
from textual.containers import Grid, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, Input, Label
from textual.binding import Binding
from cdp_cluster_sizing import estimate_cluster_sizing, FlinkJob, FlinkService
from decimal import Decimal
import re


class NumberInput(Input):
    def on_key(self, event: events.Key) -> None:
        # Ignore navigation keys
        if event.key in ("left", "right", "up", "down", "home", "end", "backspace", "delete"):
            return

        # Allow only digits and commas for job_tasks input
        if self.id == "job_tasks_input":
            if self.value and not re.match(r'^\d+(,\d+)*$', self.value):
                self.value = re.sub(r'[^0-9,]', '', self.value)
            return

        # Allow only digits, commas, and periods for other inputs
        if self.value and not re.match(r'^[\d,\.]+$', self.value):
            self.value = re.sub(r'[^0-9,\.]', '', self.value)


class InputGroup(Static):
    def __init__(self, id: str, message: str, default_value: str = ""):
        super().__init__()
        self.id = id
        self.message = message
        self.default_value = default_value

    def compose(self):
        yield Label(self.message)
        yield NumberInput(id=f"{self.id}_input")

    def on_mount(self):
        self.query_one(NumberInput).value = self.default_value



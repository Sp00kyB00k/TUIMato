import json
from time import monotonic
from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, Checkbox, Header, Footer, Input, Label, Rule, Static


class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        """
        Create child widgets for the app
        """
        yield Header()
        yield Timer(id="timer")
        yield Label("List of tasks", id="task_label")
        yield Rule(line_style="heavy")
        yield ScrollableContainer(id="task_container")
        yield Footer()


class SettingsScreen(Screen):
    CSS_PATH = "styling/settingsscreen.tcss"

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="settings-screen-container"):
            yield Label("Settings Menu")
            for key, value in self.app.SETTINGS.items():
                yield Container(Label(f"{key}"),  Input(placeholder=f"{value}", id=f'{key}-settings-value'))

    def on_input_submitted(self, event: Input.Submitted):
        input_id = event.input.id.split('-')[0]
        self.app.SETTINGS[input_id] = float(event.input.value)
        self.app.switch_mode('dashboard')


class HelpScreen(Screen):
    CSS_PATH = "styling/helpscreen.tcss"

    def compose(self) -> ComposeResult:
        with Container(id="help-screen-container"):
            yield Label("This is a PomoDoro App")
            yield Label("It allows for setting a timer and creating a task list")


class TaskModal(ModalScreen[str]):
    """
    Modal Screen for obtaining the task name
        returning the string value of the input
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Create a Task")
        yield Input(placeholder="A Task", validate_on=['submitted'], max_length=120, id="task_input")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted):
        self.app.TASK_LIST.append({'task_name':f'{event.input.value}'})
        self.dismiss(event.input.value)


class Timer(Static):
    """
    A Timer Widget
    """

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Event handler for when a button has been pressed.
        """
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()

    def compose(self) -> ComposeResult:
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay()


class TimeDisplay(Static):
    """
    A Widget to display Time
    """
    AUTO_FOCUS = None
    display_time = reactive(0.0)

    def __init__(self):
        super().__init__()
        self.delta_time = monotonic()
        self.time = self.app.SETTINGS['hours'] * 3600 + \
            self.app.SETTINGS['minutes'] * 60 + self.app.SETTINGS['seconds']
        self.display_time = reactive(self.time)

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(
            1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        current_time = monotonic()
        self.time = self.time - (current_time - self.delta_time)
        self.display_time = self.time
        if int(self.time) <= 0:
            self.time = 0.0
            self.app.finish_task()
            self.stop()
            self.display_time = self.time
        self.delta_time = current_time

    def watch_display_time(self) -> None:
        mins, secs = divmod(self.time, 60)
        hrs, mins = divmod(mins, 60)
        self.update(f"{hrs:02.0f}:{mins:02.0f}:{secs:02.0f}")

    def start(self) -> None:
        self.time = self.app.SETTINGS['hours'] * 3600 + \
            self.app.SETTINGS['minutes'] * 60 + self.app.SETTINGS['seconds']
        self.update_timer.resume()

    def stop(self) -> None:
        self.update_timer.pause()

    def reset(self) -> None:
        self.time = self.app.SETTINGS['hours'] * 3600 + \
            self.app.SETTINGS['minutes'] * 60 + self.app.SETTINGS['seconds']
        self.display_time = self.time


class Pomo(App):
    """
    A Textual App for keeping track of tasks and setting a timer
    """
    CSS_PATH = "styling/main.tcss"
    TITLE = "PomoDoro TUI"
    SUB_TITLE = "Collect tasks, execute and log them"

    BINDINGS = [
        ("a", "add_task", "Add Task"),
        ("r", "remove_task", "Remove Task"),
        ("f", "finish_task", "Last Task Finished"),
        ("e", "export_task", "Export Tasks to JSON"),
        ("d", "switch_mode('dashboard')", "Dashboard"),
        ("s", "switch_mode('settings')", "Settings"),
        ("h", "switch_mode('help')", "Help")
    ]

    MODES = {
        "dashboard": DashboardScreen,
        "settings": SettingsScreen,
        "help": HelpScreen
    }

    SETTINGS = {'hours': 0.0, 'minutes': 25.0, 'seconds': 0.0}
    TASK_LIST = []
    TASK_COUNTER = 0

    def on_mount(self) -> None:
        self.switch_mode("dashboard")
    
    def action_export_task(self) -> None:
        with open('pomodoro_task_list', 'w') as f:
            f.write(json.dumps(self.TASK_LIST))

    def action_add_task(self) -> None:
        """
        Action to display the Input Modal for the Tasks.
        """

        def obtain_task_input(task_name: str) -> None:
            """
            Called when TaskModal is dismissed
            """
            self.query_one("#task_container").mount(
                Checkbox(task_name, id=f"task-{self.TASK_COUNTER}"))
            self.TASK_COUNTER += 1
        self.switch_mode("dashboard")
        self.push_screen(TaskModal(), obtain_task_input)

    def action_remove_task(self) -> None:
        tasks = self.query(f"#task-{self.TASK_COUNTER}")
        if tasks:
            tasks.last().remove()
            self.TASK_COUNTER -= 1

    def action_finish_task(self) -> None:
        self.finish_task()

    def finish_task(self) -> None:
        try:
            for task_number in range(0, len(self.TASK_LIST) + 1): 
                task = self.query_one(f"#task-{task_number}")
                if task.value ==  True:
                    continue
                else:
                    task.value = True
                    break
        except:
            pass

if __name__ == "__main__":
    app = Pomo()
    app.run()

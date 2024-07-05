from time import monotonic
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Button, Checkbox, Header, Footer, Input, Label, Rule, Static


class Pomo(App):
    """
    A Textual App for keeping track of tasks and setting a timer
    """
    CSS_PATH = "pomo.tcss"
    TITLE = "PomoDoro TUI"
    SUB_TITLE = "Collect tasks, execute and log them"

    BINDINGS = [
        ("a", "add_timer", "Add Timer"),
        ("r", "remove_timer", "Remove Timer"),
    ]

    def compose(self) -> ComposeResult:
        """
        Create child widgets for the app
        """
        yield Header()
        yield ScrollableContainer(Timer(), id="timers")
        yield ScrollableContainer(Tasks(), id="tasks")
        yield Footer()

    def action_add_timer(self) -> None:
        new_timer = Timer()
        self.query_one("#timers").mount(new_timer)
        new_timer.scroll_visible()

    def action_remove_timer(self) -> None:
        timers = self.query("Timer")
        if timers:
            timers.last().remove()


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
    minutes = 25.0 * 60.0
    seconds = 0
    pomo_time = minutes + seconds
    delta_time = monotonic()
    time = reactive(pomo_time)

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(
            1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        t = monotonic()
        self.time -= (t - self.delta_time)
        self.delta_time = t

    def watch_time(self, current_time: float) -> None:
        mins, secs = divmod(current_time, 60)
        hrs, mins = divmod(mins, 60)
        self.update(f"{hrs:02.0f}:{mins:02.0f}:{secs:02.0f}")

    def start(self) -> None:
        self.pomo_time = self.minutes + self.seconds
        self.update_timer.resume()

    def stop(self) -> None:
        self.update_timer.pause()

    def reset(self) -> None:
        self.time = self.pomo_time


class Tasks(Static):
    def compose(self) -> ComposeResult:
        yield Label("Tasks")
        yield Rule(line_style="heavy")
        yield TaskDisplay()


class TaskDisplay(Static):
    def compose(self) -> ComposeResult:
        yield Checkbox("Name of the tasks")
        yield Input()


if __name__ == "__main__":
    app = Pomo()
    app.run()

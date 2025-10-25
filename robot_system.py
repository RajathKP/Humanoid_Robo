"""

Humanoid Robot Reception Assistant (CLI simulation)

"""

from collections import deque
from datetime import datetime
import random
import time


class Visitor:
    """Simple data class for a visitor."""
    def __init__(self, name: str):
        self.name = name.strip()

    def __repr__(self):
        return f"Visitor(name={self.name})"


class VisitorLog:
    """Maintains a chronological list of visitor interactions (append-only)."""
    def __init__(self):
        self._entries = []  # list of dicts: {'name':..., 'time':..., 'action':...}

    def record(self, name: str, action: str):
        entry = {
            'name': name,
            'time': datetime.now().isoformat(timespec='seconds'),
            'action': action
        }
        self._entries.append(entry)
        return entry

    def all_entries(self):
        """Return a copy of log entries."""
        return list(self._entries)

    def __repr__(self):
        return f"VisitorLog(entries={len(self._entries)})"



class AppointmentStack:
    """
       Preloaded appointment list implemented as a stack (LIFO).
       The spec requested a stack for validating names; we implement push/pop and a check method.
       """
    def __init__(self, names=None):
        self._stack = []
        if names:
            # Push initial appointments so that last name in the list is on top of stack.
            for n in names:
                self.push(n)

    def push(self, name: str):
        self._stack.append(name.strip())

    def pop(self):
        if self._stack:
            return self._stack.pop()
        return None

    def peek(self):
        return self._stack[-1] if self._stack else None

    def contains(self, name: str) -> bool:
        """Check if name exists anywhere in the stack."""
        return name.strip() in self._stack

    def __len__(self):
        return len(self._stack)

    def __repr__(self):
        return f"AppointmentStack(size={len(self)})"


class VisitorQueue:
    """Queue to manage visitors in first-come-first-served order."""
    def __init__(self):
        self._q = deque()

    def enqueue(self, visitor: Visitor):
        self._q.append(visitor)

    def dequeue(self):
        return self._q.popleft() if self._q else None

    def peek(self):
        return self._q[0] if self._q else None

    def __len__(self):
        return len(self._q)

    def list_all(self):
        return list(self._q)

    def __repr__(self):
        return f"VisitorQueue(size={len(self)})"


class SensorSuite:
    """
    Simulates environment sensors with pseudo-random data.
    Produces temperature (°C), noise level (dB), and ambient light (lux).

    """
    def __init__(self, temp_base=22.0, noise_base=35.0, light_base=300.0):
        self.temp_base = temp_base
        self.noise_base = noise_base
        self.light_base = light_base

    def read_temperature(self) -> float:
        # simulate mild fluctuations
        return round(self.temp_base + random.uniform(-3.0, 3.0), 1)

    def read_noise(self) -> float:
        return round(self.noise_base + random.uniform(-20.0, 20.0), 1)

    def read_light(self) -> float:
        return round(self.light_base + random.uniform(-150.0, 150.0), 1)

    def read_all(self) -> dict:
        return {
            'temperature_c': self.read_temperature(),
            'noise_db': self.read_noise(),
            'light_lux': self.read_light(),
            'timestamp': datetime.now().isoformat(timespec='seconds')
        }


class HumanoidRobot:

    def __init__(self, appointment_names=None):
        self.appointments = AppointmentStack(appointment_names or [])
        self.queue = VisitorQueue()
        self.log = VisitorLog()
        self.sensors = SensorSuite()
        self.state = 'idle'  # states: idle, engaged, guiding, monitoring

    @staticmethod
    def prompt_welcome():
        return "Hello! I'm E-Assist, your reception robot. How can I help you today?"

    def check_appointment(self, name: str) -> bool:
        """Validate visitor against appointments (stack)."""
        exists = self.appointments.contains(name)
        return exists

    def greet_visitor(self, visitor: Visitor) -> str:
        """Greet visitor, validate, and optionally add to queue/log."""
        self.state = 'engaged'
        greeting = f"Hello, {visitor.name}! Nice to meet you."
        if self.check_appointment(visitor.name):
            greeting += " I see you have an appointment. I'll guide you shortly."
            action = 'greeted_with_appointment'
        else:
            greeting += " I don't see an appointment under that name. I'll add you to the waiting queue."
            action = 'greeted_no_appointment'
            self.queue.enqueue(visitor)
        self.log.record(visitor.name, action)
        # After greeting, robot returns to idle (unless guiding)
        self.state = 'idle'
        return greeting

    def guide_next_in_queue(self) -> str:
        """Simulates guiding the next visitor in queue (if any)."""
        if len(self.queue) == 0:
            return "No visitors in the waiting queue."
        self.state = 'guiding'
        next_visitor = self.queue.dequeue()
        # Simulate navigation with a tiny sleep to mimic doing a task
        nav_time = random.uniform(0.5, 1.2)
        time.sleep(nav_time)  # short sleep for realism in CLI simulation
        msg = f"Guiding {next_visitor.name} to their meeting room. (navigation took {nav_time:.2f}s)"
        self.log.record(next_visitor.name, 'guided_to_room')
        self.state = 'idle'
        return msg

    def monitor_environment(self) -> dict:
        """Reads sensors and returns a dict of readings; records notable alerts on stack-like alert structure."""
        self.state = 'monitoring'
        data = self.sensors.read_all()
        # Simple rule-based responses:
        alerts = []
        if data['temperature_c'] > 28:
            alerts.append('high_temperature')
            self.log.record('environment', f"alert:{alerts[-1]}:{data['temperature_c']}")
        if data['noise_db'] > 70:
            alerts.append('loud_noise')
            self.log.record('environment', f"alert:{alerts[-1]}:{data['noise_db']}")
        if data['light_lux'] < 50:
            alerts.append('low_light')
            self.log.record('environment', f"alert:{alerts[-1]}:{data['light_lux']}")
        self.state = 'idle'
        return {'readings': data, 'alerts': alerts}

    def get_visitor_log(self):
        return self.log.all_entries()

    def preload_appointment(self, name: str):
        """Allow adding new appointment to the stack."""
        self.appointments.push(name)
        return f"Appointment for '{name}' added."

    def __repr__(self):
        return f"HumanoidRobot(state={self.state}, appointments={len(self.appointments)}, queue={len(self.queue)})"


def cli_run(robot: HumanoidRobot):
    """Simple CLI loop for interacting with the robot."""
    print(robot.prompt_welcome())
    actions = {
        '1': 'Register visitor / Greet',
        '2': 'Guide next visitor',
        '3': 'Monitor environment',
        '4': 'Show visitor log',
        '5': 'Preload appointment (for testing)',
        'q': 'Quit'
    }
    while True:
        print("\nAvailable actions:")
        for k, v in actions.items():
            print(f" {k}) {v}")
        choice = input("Choose action: ").strip().lower()
        if choice == '1':
            name = input("Enter visitor name: ").strip()
            if not name:
                print("Name cannot be empty.")
                continue
            visitor = Visitor(name)
            print(robot.greet_visitor(visitor))
        elif choice == '2':
            print(robot.guide_next_in_queue())
        elif choice == '3':
            result = robot.monitor_environment()
            print("Sensor readings:", result['readings'])
            if result['alerts']:
                print("Alerts:", ", ".join(result['alerts']))
            else:
                print("No alerts.")
        elif choice == '4':
            logs = robot.get_visitor_log()
            if not logs:
                print("Log is empty.")
            else:
                print("Visitor Log:")
                for e in logs:
                    print(f" - {e['time']}: {e['name']} -> {e['action']}")
        elif choice == '5':
            name = input("Name to add to appointments: ").strip()
            if name:
                print(robot.preload_appointment(name))
            else:
                print("Name empty; not added.")
        elif choice == 'q':
            print("Shutting down. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


# Allow running as script

if __name__ == '__main__':
    # Preload a few appointments as test data
    initial_appointments = ["Alice Johnson", "Bob Smith", "Charlie Li"]
    robot = HumanoidRobot(initial_appointments)
    cli_run(robot)

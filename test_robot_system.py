"""
Unit tests for robot_system.py
"""

import unittest
from robot_system import HumanoidRobot, Visitor, AppointmentStack


class TestHumanoidRobot(unittest.TestCase):
    def setUp(self):
        self.app_names = ["Alice Johnson", "Bob Smith"]
        self.robot = HumanoidRobot(self.app_names)

    def test_preload_and_check_appointment(self):
        # initially contains Alice and Bob
        self.assertTrue(self.robot.check_appointment("Alice Johnson"))
        self.assertTrue(self.robot.check_appointment("Bob Smith"))
        # preload new name and check
        self.robot.preload_appointment("Zoe Blaze")
        self.assertTrue(self.robot.check_appointment("Zoe Blaze"))

    def test_greet_with_and_without_appointment(self):
        visitor1 = Visitor("Alice Johnson")
        msg1 = self.robot.greet_visitor(visitor1)
        self.assertIn("appointment", msg1.lower())
        # Non-appointment visitor should be queued and logged
        visitor2 = Visitor("Derek")
        msg2 = self.robot.greet_visitor(visitor2)
        self.assertIn("waiting queue", msg2.lower())
        # queue should have size 1
        self.assertEqual(len(self.robot.queue), 1)

    def test_guide_next_in_queue(self):
        # Add one visitor and then guide
        visitor = Visitor("NoAppointmentPerson")
        self.robot.queue.enqueue(visitor)
        before = len(self.robot.queue)
        result = self.robot.guide_next_in_queue()
        # After guiding queue decreases
        self.assertEqual(len(self.robot.queue), max(0, before - 1))
        self.assertIn("Guiding", result)

    def test_monitor_environment_returns_readings(self):
        data = self.robot.monitor_environment()
        self.assertIn('readings', data)
        self.assertIn('temperature_c', data['readings'])


if __name__ == '__main__':
    unittest.main()

"""
motor_ball_queue_two_turns.py
---
This file contains the MotorBallQueue class, which controls the Ball Queue Motor (BQM).
NOTE: This is the file that is not being used by the current iteration of the project as of Spring Semester 2021 simply because it was found that moving the queue once (as done in motor_ball_queue_turn_once.py) is sufficient enough for ensuring only 1 ball drops at a time.
---

Author: Andrei Biswas (@codeabiswas)
Date: May 4, 2021
Last Modified: May 04, 2021
"""

import time

import Jetson.GPIO as gpio


class MotorBallQueue:
    """The BQM Motor will be controlled using the 'Move to Incremental Distance (2 Distance, Home To Switch)' Setting.
    """

    def __init__(self):
        """Any motor intiialization code will go here
        Enable Pin: Pin 37- Energizes the motor
        Input A: Pin 40 - Selects the position (0 is pos. 1 and 1 is pos. 2)
        Input B: Pin 2 (5V)
        HLFB: Pin 12
        """

        # Board pin-numbering scheme
        gpio.setmode(gpio.BOARD)

        # Assign pin numbers to respective signals
        self.en_pin = 37
        self.in_a_pin = 40

        # Set up channels
        # Enable pin set to low (unenergized)
        # Input A pin set to low (Position 1)
        self.bqm_channels = [self.en_pin, self.in_a_pin]
        gpio.setup(self.bqm_channels, gpio.OUT, initial=gpio.LOW)

        # This variable will track whether or not the motor is energized
        self.motor_on = False

        # This variable is the amount of time for triggering enable
        self.en_trig_time = 0.02

    def energize_motor(self):
        """Turns the motor on
        """
        # Set Enable pin to high to energize motor
        gpio.output(self.en_pin, gpio.HIGH)

        # Motor is now energized
        self.motor_on = True

    def pulse_enable(self):
        """Pulsing the enable pin is how this motor knows to move the distance selected by Input A
        """
        gpio.output(self.en_pin, gpio.LOW)
        time.sleep(self.en_trig_time)
        gpio.output(self.en_pin, gpio.HIGH)

    def turn_once_half(self):
        """BQM turns half a rotation which allows one ball to fall
        """

        # Set Input A to high to move half distance
        gpio.output(self.in_a_pin, gpio.HIGH)
        self.pulse_enable()

    def turn_once_full(self):
        """BQM turns a rotation which allows one ball to fall
        """

        # Set Input A to low to move
        gpio.output(self.in_a_pin, gpio.LOW)
        self.pulse_enable()

    def get_motor_state(self):
        """Returns whether or not the motor is energized
        Returns:
            self.motor_on: [bool]: True if the motor is on, False otherwise
        """
        return self.motor_on

    def stop_and_reset_motor(self):
        """Stops the motor and resets all previously set values to their default values
        """

        # Turn BQ half a rotation
        self.turn_once_half()

        # Set Input A to low to move to position 1
        gpio.output(self.in_a_pin, gpio.LOW)

        # Turn off motor
        gpio.output(self.en_pin, gpio.LOW)

        # Clean all BQM-related channels
        # NOTE: Doing this means the pins have been set to their default state, and init method needs to be called again to make this motor work
        gpio.cleanup(self.bqm_channels)

        # Motor is not energized
        self.motor_on = False


def main():
    """main.

    Main prototype/testing area. Code prototyping and checking happens here.
    """

    # Initialize object
    motor_bqm = MotorBallQueue()
    # Turn motor on
    motor_bqm.energize_motor()
    # Get energized state of motor
    print(motor_bqm.get_motor_state())
    # Turn the queue 3 times for 3 balls to fall
    for turn in range(3):
        if turn == 0:
            motor_bqm.turn_once_half()
        else:
            # Move motor forwards
            motor_bqm.turn_once_full()
        time.sleep(2)
    # Reset motor
    motor_bqm.stop_and_reset_motor()
    # Get energized state of motor
    print(motor_bqm.get_motor_state())


if __name__ == "__main__":
    # Run the main function
    main()

"""
motor_flywheel_top.py
---
This file contains the MotorFlywheelTop class, which controls the Flywheel Top Motor (FTM) using Pulse-Width Modulation (PWM).
---

Author: Andrei Biswas (@codeabiswas)
Date: May 4, 2021
Last Modified: May 04, 2021
"""

import math
import time

import Jetson.GPIO as gpio


class MotorFlywheelTop:
    """The Top Flywheel Motor will be controlled using the 'Unipolar PWM command'. This motor will be running counter-clockwise.
    """

    def __init__(self):
        """Any motor intiialization code will go here

        Enable Pin: Pin 29 - Energizes the motor
        Input A: Pin 6 (GND) [selects counter-clockwise polarity]
        Input B: Pin 32 (PWM0)
        HLFB: Pin 11 - ASG Velocity

        """

        # The flywheel's diameter (in inches)
        self.flywheel_diam = 16.5
        # The flywheel's circumference (in inches)
        self.flywheel_circ = self.flywheel_diam * math.pi
        # The flywheel motor's max RPM
        self.fm_max_rpm = 3180

        # Board pin-numbering scheme
        gpio.setmode(gpio.BOARD)

        # Assign pin numbers to respective signals
        self.en_pin = 29
        self.in_b_pin = 32
        self.hlfb_pin = 11

        # PWM frequency set to 1 kHz
        self.pwm_freq = 1000

        # Set up channels
        # Enable pin set to low (unenergized)
        # Input B pin set to low
        # HLFB pin set as input
        self.ftm_out_channels = [self.en_pin, self.in_b_pin]
        gpio.setup(self.ftm_out_channels, gpio.OUT, initial=gpio.LOW)
        gpio.setup(self.hlfb_pin, gpio.IN)

        # Initialize PWM w/ frequency
        self.pwm = gpio.PWM(self.in_b_pin, self.pwm_freq)
        # Start PWM at 0% Duty Cycle
        self.pwm.start(0)

        # This variable will track whether or not the motor is energized
        self.motor_on = False

    def energize_motor(self):
        """Turns the motor on
        """
        # Set Enable pin to high to energize motor
        gpio.output(self.en_pin, gpio.HIGH)

        # Motor is now energized
        self.motor_on = True

    def set_speed(self, desired_speed):
        """Set the speed of the motor

        Args:
            desired_speed ([int]): The speed for the top flywheel motor (in MPH)
        """

        inch_per_mile = 63360
        min_per_hour = 60

        # Calculate RPM based on desired speed
        desired_rpm = (desired_speed*inch_per_mile) / \
            (self.flywheel_circ*min_per_hour)

        print("Speed: {} to RPM: {}".format(desired_speed, desired_rpm))

        # Find out how much percentage that RPM is to the max RPM of the motor
        req_duty_cycle = int((desired_rpm/self.fm_max_rpm)*100)

        print("Hence, duty cycle: {}".format(req_duty_cycle))

        # Change duty cycle to that percentage
        self.pwm.ChangeDutyCycle(req_duty_cycle)

        # Block thread until speed has been set or timeout of 10 seconds has been reached (whichever is first)
        gpio.wait_for_edge(self.hlfb_pin, gpio.RISING, timeout=2000)

        return True

    def hlfb_output(self):
        """Returns whether the required speed has been attained  by the motor's encoder (using HLFB: ASG velocity)

        NOTE: This currently does not work since Teknic does not support this HLFB mode for this velocity mode anymore
        """

        return gpio.input(self.hlfb_pin)

    def get_motor_state(self):
        """Returns whether or not the motor is energized

        Returns:
            self.motor_on: [bool]: True if the motor is on, False otherwise
        """
        return self.motor_on

    def stop_and_reset_motor(self):
        """Stops the motor and resets all previously set values to their default values
        """

        # Set Input B to low
        self.pwm.ChangeDutyCycle(0)

        # Unenergize the motor
        gpio.output(self.en_pin, gpio.LOW)

        # Clean all FTM-related channels
        # NOTE: Doing this means the pins have been set to their default state, and init method needs to be called again to make this motor work
        gpio.cleanup(self.ftm_out_channels)
        gpio.cleanup(self.hlfb_pin)

        # Motor is not energized
        self.motor_on = False


def main():
    """main.

    Main prototype/testing area. Code prototyping and checking happens here.
    """

    # Initialize object
    motor_top_flywheel = MotorFlywheelTop()
    # Turn motor on
    motor_top_flywheel.energize_motor()
    # Get energized state of motor
    print(motor_top_flywheel.get_motor_state())
    # Set speeds 30-100 mph per 5 mph increment
    # for speed in range(30, 105, 5):
    for speed in range(1, 4):
        print("Executing {} mph".format(speed))
        # As long as speed is not set
        motor_top_flywheel.set_speed(speed)
        # When speed has been set
        print("Speed {} mph set".format(speed))
        # HLFB should be High
        print(motor_top_flywheel.hlfb_output())
    # Reset motor
    motor_top_flywheel.stop_and_reset_motor()
    # Get energized state of motor
    print(motor_top_flywheel.get_motor_state())


if __name__ == "__main__":
    # Run the main function
    main()

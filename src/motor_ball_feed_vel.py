import time

import Jetson.GPIO as gpio


class MotorBallFeed:
    """The Ball Feed Motor will be controlled using the 'Move to Absolute Position (2-Position, Home to Switch)' Setting. As Teknik puts it, 'this mode was designed for replacing hydraulic or pnewmatic cylinders that move between two positions'
    """

    def __init__(self):
        """Any motor intiialization code will go here

        Enable Pin: Pin 36 - Energizes the motor
        Input A: Pin 38 - Selects the position (0 is pos. 1 and 1 is pos. 2)
        Input B: Pin 6 (GND)
        HLFB: Pin 6 (GND)
        """

        # Board pin-numbering scheme
        gpio.setmode(gpio.BOARD)

        # Assign pin numbers to respective signals
        self.en_pin = 36
        self.in_a_pin = 38

        # Set up channels
        # Enable pin set to low (unenergized)
        # Input A pin set to low (Position 1)
        self.bfm_channels = [self.en_pin, self.in_a_pin]
        gpio.setup(self.bfm_channels, gpio.OUT, initial=gpio.LOW)

        # This variable will track whether or not the motor is energized
        self.motor_on = False

        # This variable will store the position of the motor (By default, it should be at pos. 1)
        self.bfm_pos = 1

    def energize_motor(self):
        """Turns the motor on
        """
        # Set Enable pin to high to energize motor
        gpio.output(self.en_pin, gpio.HIGH)

        # Motor is now energized
        self.motor_on = True

    def move_forward(self, rof_time=1):
        """Feed moves forward (pos. 2)
        """
        # XX - A B
        # Forward: 10
        # Backward: 00

        # Set Input A to high to move to position 2
        gpio.output(self.in_a_pin, gpio.HIGH)
        # Set Enable pin to high to energize motor
        gpio.output(self.en_pin, gpio.HIGH)
        time.sleep(rof_time)
        # Set Enable pin to low to stop energizing motor
        gpio.output(self.en_pin, gpio.LOW)

        # Update the state of position variable
        self.bfm_pos = 2

    def move_backward(self,rof_time=1):
        """Feed moves backward (pos. 1)
        """

        # Set Input A to high to move to position 2
        gpio.output(self.in_a_pin, gpio.LOW)
        # Set Enable pin to high to energize motor
        gpio.output(self.en_pin, gpio.HIGH)
        time.sleep(rof_time)
        # Set Enable pin to low to stop energizing motor
        gpio.output(self.en_pin, gpio.LOW)

        # Update the state of position variable
        self.bfm_pos = 1

    def get_motor_state(self):
        """Returns whether or not the motor is energized

        Returns:
            self.motor_on: [bool]: True if the motor is on, False otherwise
        """
        return self.motor_on

    def get_pos(self):
        """Returns the current position of the feed motor

        Returns:
            self.bfm_pos [int]: Number is analogous to position (1 -> pos. 1 and 2 -> pos. 2)
        """
        return self.bfm_pos

    def stop_and_reset_motor(self):
        """Stops the motor and resets all previously set values to their default values
        """

        # # Set Input A to low to move to position 1
        # gpio.output(self.in_a_pin, gpio.LOW)

        # Unenergize the motor
        gpio.output(self.en_pin, gpio.LOW)

        # Update the state of position variable
        self.bfm_pos = 1

        # Clean all BFM-related channels
        # NOTE: Doing this means the pins have been set to their default state, and init method needs to be called again to make this motor work
        gpio.cleanup(self.bfm_channels)

        # Motor is not energized
        self.motor_on = False

def main():
    # Initialize object
    motor_ball_feed = MotorBallFeed()
    # time.sleep(2)
    # Turn motor on
    # motor_ball_feed.energize_motor()
    # Get energized state of motor
    # print(motor_ball_feed.get_motor_state())
    time.sleep(2)
    # Move motor forwards
    motor_ball_feed.move_forward(rof_time=2.5)
    # Get position
    print(motor_ball_feed.get_pos())
    time.sleep(2)
    # Move motor backwards
    motor_ball_feed.move_backward(rof_time=2.5)
    # # Get position
    print(motor_ball_feed.get_pos())
    time.sleep(2)
    # Reset motor
    motor_ball_feed.stop_and_reset_motor()
    # # Get energized state of motor
    print(motor_ball_feed.get_motor_state())


if __name__ == "__main__":
    main()

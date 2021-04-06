import Jetson.GPIO as gpio

class MotorYaw:
    """The Ball Feed Motor will be controlled using the 'Move to Absolute Position (2-Position, Home to Switch)' Setting. As Teknik puts it, 
    'this mode was designed for replacing hydraulic or pnewmatic cylinders that move between two positions'
    """

    def init(self):
        """Any motor intiialization code will go here
        Enable Pin: Pin 24 - Energizes the motor
        Input A: Pin 26 - Selects the position (0 is pos. 1 and 1 is pos. 2)
        Input B: Pin 6 (GND)
        HLFB: Pin 22
        """

        # Board pin-numbering scheme
        gpio.setmode(gpio.BOARD)

        # Assign pin numbers to respective signals
        self.en_pin = 24
        self.in_a_pin = 26

        # Set up channels
        # Enable pin set to low (unenergized)
        # Input A pin set to low (Position 1)
        self.ym_channels = [self.en_pin, self.in_a_pin]
        gpio.setup(self.ym_channels, gpio.OUT, initial=gpio.LOW)

        # This variable will track whether or not the motor is energized
        self.motor_on = False

        # This variable will store the position of the motor (By default, it should be at pos. 1)
        self.ym_pos = 1

    def energize_motor(self):
        """Turns the motor on
        """
        # Set Enable pin to high to energize motor
        gpio.output(self.en_pin, gpio.HIGH)

        # Motor is now energized
        self.motor_on = True

    def move_forward(self):
        """Feed moves forward (pos. 2)
        """

        # Set Input A to high to move to position 2
        gpio.output(self.in_a_pin, gpio.HIGH)

        # Update the state of position variable
        self.ym_pos = 2

    def move_backward(self):
        """Feed moves backward (pos. 1)
        """

        # Set Input A to low to move to position 1
        gpio.output(self.in_a_pin, gpio.LOW)

        # Update the state of position variable
        self.ym_pos = 1

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
        return self.ym_pos

    def stop_and_reset_motor(self):
        """Stops the motor and resets all previously set values to their default values
        """

        # Unenergize the motor
        #CONFUSION seems like htis just turns off the motor and can't this just be done in the cleanup line
        gpio.output(self.en_pin, gpio.LOW)

        # Set Input A to low to move to position 1
        gpio.output(self.in_a_pin, gpio.LOW)

        # Update the state of position variable
        self.ypos = 1

        # Clean all BFM-related channels
        # NOTE: Doing this means the pins have been set to their default state, and init method needs to be called again to make this motor work
        gpio.cleanup(self.ym_channels)

        # Motor is not energized
        self.motor_on = False


def main():
    # Initialize object
    motor_yaw = MotorYaw()
    # Turn motor on
    motor_yaw.energize_motor()
    # Get energized state of motor
    print(motor_yaw.get_motor_state())
    # Move motor forwards
    motor_yaw.move_forward()
    # Get position
    print(motor_yaw.get_pos())
    # Move motor backwards
    motor_yaw.move_backward()
    # Get position
    print(motor_yaw.get_pos())
    # Reset motor
    motor_yaw.stop_and_reset_motor()
    # Get energized state of motor
    print(motor_yaw.get_motor_state())


if __name__ == "__main__":
    main()
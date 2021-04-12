import time

import Jetson.GPIO as gpio


class MotorYaw:
    """
    """

    def __init__(self):
        """Any motor intiialization code will go here
        Enable Pin: Pin 24 - Energizes the motor
        Input A: Pin 26 - Selects the distance (0 is dist. 1 and 1 is dist. 2)
        Input B: Pin 6 (GND)
        HLFB: Pin 22
        """

        # Board pin-numbering scheme
        gpio.setmode(gpio.BOARD)

        # Assign pin numbers to respective signals
        self.en_pin = 24
        self.in_a_pin = 26
        self.hlfb_pin = 22

        # Set up channels
        # Enable pin set to low (unenergized)
        # Input A pin set to low (Position 1)
        # HLFB pin set as input
        self.ym_channels = [self.en_pin, self.in_a_pin]
        gpio.setup(self.ym_channels, gpio.OUT, initial=gpio.LOW)
        gpio.setup(self.hlfb_pin, gpio.IN)

        # This variable will track whether or not the motor is energized
        self.motor_on = False

        # Stores how many degrees yaw mechanism moves with one rotation of the motor
        self.rotation_to_degree = 10

        # This variable will store the position of the motor (By default, it should be centered - cnt. 0)
        self.curr_encoder_count = 0

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

    def move_right(self, degree, num_pulses=None):
        """Yaw motor moves right by X degree
        """

        if num_pulses is None:
            # Calculate how many movements we need to achieve that degree
            num_pulses = abs(int(degree/self.rotation_to_degree))

        # Set Input A to high to move distance 2
        gpio.output(self.in_a_pin, gpio.HIGH)

        for _ in range(num_pulses):
            self.pulse_enable()

        # Block the thread until rising edge has been detected OR 10 seconds have passed (whichever is first)
        gpio.wait_for_edge(self.hlfb_pin, gpio.RISING, timeout=10000)

        # Update the state of position variable
        self.curr_encoder_count += num_pulses

    def move_left(self, degree, num_pulses=None):
        """Yaw motor moves left by X degree
        """

        if num_pulses is None:
            # Calculate how many movements we need to achieve that degree
            num_pulses = abs(int(degree/self.rotation_to_degree))

        # Set Input A to high to move distance 1
        gpio.output(self.in_a_pin, gpio.LOW)

        for _ in range(num_pulses):
            self.pulse_enable()

        # Block the thread until rising edge has been detected OR 10 seconds have passed (whichever is first)
        gpio.wait_for_edge(self.hlfb_pin, gpio.RISING, timeout=10000)

        # Update the state of position variable
        self.curr_encoder_count -= num_pulses

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
        return self.curr_encoder_count

    def reset_yaw(self):
        """Resets the yaw motor to center
        """

        # Yaw motor facing right, so move the opposite direction to reset
        if self.curr_encoder_count > 0:
            self.move_left(degree=None, num_pulses=self.curr_encoder_count)
        # Yaw motor facing left, so move the opposite direction to reset
        elif self.curr_encoder_count < 0:
            self.move_right(degree=None, num_pulses=self.curr_encoder_count)

    def stop_and_reset_motor(self):
        """Stops the motor and resets all previously set values to their default values
        """

        # Reset the yaw motor
        self.reset_yaw()

        # Set Input A to low to move to position 1
        gpio.output(self.in_a_pin, gpio.LOW)

        # Unenergize the motor
        gpio.output(self.en_pin, gpio.LOW)

        # Clean all YM-related channels
        # NOTE: Doing this means the pins have been set to their default state, and init method needs to be called again to make this motor work
        gpio.cleanup(self.ym_channels)
        gpio.cleanup(self.hlfb_pin)

        # Motor is not energized
        self.motor_on = False


def main():
    # Initialize object
    motor_yaw = MotorYaw()
    # Turn motor on
    motor_yaw.energize_motor()
    # Get energized state of motor
    print(motor_yaw.get_motor_state())
    time.sleep(2)
    # Move motor right 90 degrees
    motor_yaw.move_right(degree=90)
    # Get position
    print(motor_yaw.get_pos())
    time.sleep(2)
    # Move motor left 90 degrees
    motor_yaw.move_left(degree=90)
    # Get position
    print(motor_yaw.get_pos())
    time.sleep(2)
    # Reset motor
    motor_yaw.stop_and_reset_motor()
    # Get energized state of motor
    print(motor_yaw.get_motor_state())


if __name__ == "__main__":
    main()

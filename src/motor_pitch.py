import time

import Jetson.GPIO as gpio


class MotorPitch:
    """The PM Motor will be controlled using the 'Move to Move to Incremental Distance (2 Distance, Home To Switch)' Setting. As Teknik puts it,
    'this mode was designed for replacing hydraulic or pnewmatic cylinders that move between two positions'
    """

    def __init__(self):
        """Any motor intiialization code will go here
        Enable Pin: Pin 21- Energizes the motor
        Input A: Pin 23 - Selects the position (0 is pos. 1 and 1 is pos. 2)
        Input B: Pin 6 (GND)
        HLFB: Pin 19
        """

        # Board pin-numbering scheme
        gpio.setmode(gpio.BOARD)

        # Assign pin numbers to respective signals
        self.en_pin = 21
        self.in_a_pin = 23

        # Set up channels
        # Enable pin set to low (unenergized)
        # Input A pin set to low (Position 1)
        self.pm_channels = [self.en_pin, self.in_a_pin]
        gpio.setup(self.pm_channels, gpio.OUT, initial=gpio.LOW)

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

    def pitch_up(self, degree, num_pulses=None):
        """Pitch motor pitches up by X degree
        """

        if num_pulses is None:
            # Calculate how many movements we need to achieve that degree
            num_pulses = abs(int(degree/self.rotation_to_degree))

        # Set Input A to high to move distance 2
        gpio.output(self.in_a_pin, gpio.HIGH)

        for _ in range(num_pulses):
            self.pulse_enable()

        # Update the state of position variable
        self.curr_encoder_count += num_pulses

    def pitch_down(self, degree, num_pulses=None):
        """Yaw motor moves left by X degree
        """

        if num_pulses is None:
            # Calculate how many movements we need to achieve that degree
            num_pulses = abs(int(degree/self.rotation_to_degree))

        # Set Input A to high to move distance 1
        gpio.output(self.in_a_pin, gpio.LOW)

        for _ in range(num_pulses):
            self.pulse_enable()

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

    def reset_pitch(self):
        """Resets the pitch motor to center
        """

        # Pitch motor facing up, so move the opposite direction to reset
        if self.curr_encoder_count > 0:
            self.pitch_down(degree=None, num_pulses=self.curr_encoder_count)
        # Pitch motor facing down, so move the opposite direction to reset
        elif self.curr_encoder_count < 0:
            self.pitch_up(degree=None, num_pulses=self.curr_encoder_count)

    def stop_and_reset_motor(self):
        """Stops the motor and resets all previously set values to their default values
        """

        # Reset pitch to 0
        self.reset_pitch()

        # Set Input A to low to move to position 1
        gpio.output(self.in_a_pin, gpio.LOW)

        # Unenergize the motor
        gpio.output(self.en_pin, gpio.LOW)

        # Clean all YM-related channels
        # NOTE: Doing this means the pins have been set to their default state, and init method needs to be called again to make this motor work
        gpio.cleanup(self.pm_channels)

        # Motor is not energized
        self.motor_on = False


def main():
    # Initialize object
    motor_pitch = MotorPitch()
    # Turn motor on
    motor_pitch.energize_motor()
    # Get energized state of motor
    print(motor_pitch.get_motor_state())
    time.sleep(2)
    # Move motor up 60 degrees
    motor_pitch.pitch_up(degree=10)
    # Get position
    print(motor_pitch.get_pos())
    time.sleep(2)
    # Move motor down 60 degrees
    motor_pitch.pitch_down(degree=10)
    # Get position
    print(motor_pitch.get_pos())
    time.sleep(2)
    # Reset motor
    motor_pitch.stop_and_reset_motor()
    # Get energized state of motor
    print(motor_pitch.get_motor_state())


if __name__ == "__main__":
    main()

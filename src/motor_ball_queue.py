class MotorBallQueue:
 """The BQM Motor will be controlled using the 'Move to Incremental Distance (1 Distance, Home To Switch)' Setting. As Teknik puts it, 
    'this mode was designed for replacing hydraulic or pnewmatic cylinders that move between two positions'
    """

    def init(self):
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

        # This variable will store the position of the motor (By default, it should be at pos. 1)
        self.bqm_pos = 0
    
    def energize_motor(self):
        """Turns the motor on
        """
        # Set Enable pin to high to energize motor
        gpio.output(self.en_pin, gpio.HIGH)
        
        #Initialize pos
        self.bqm_pos = 0
        # Motor is now energized
        self.motor_on = True    
    
    def move_forward(self):
        """Feed moves forward (pos. 2)
        """

        # Set Input A to high to move to position 2
        gpio.output(self.in_a_pin, gpio.HIGH)

        #Increment pos
        self.bqm_pos += 1   

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
        return self.bqm_pos

    def stop_and_reset_motor(self):
        """Stops the motor and resets all previously set values to their default values
        """
        
        #Turn off motor
        gpio.output(self.en_pin, gpio.LOW)
        # Set Input A to low to move to position 1
        gpio.output(self.in_a_pin, gpio.LOW)

        # Clean all BFM-related channels
        # NOTE: Doing this means the pins have been set to their default state, and init method needs to be called again to make this motor work
        gpio.cleanup(self.pm_channels)

        # Motor is not energized
        self.motor_on = False

def main():
    # Initialize object
    motor_bqm = MotorBallQueue()
    # Turn motor on
    motor_bqm.energize_motor()
    # Get energized state of motor
    print(motor_bqm.get_motor_state())
    # Move motor forwards
    motor_bqm.move_forward()
    # Get position
    print(motor_bqm.get_pos())
    # Move motor forwards
    motor_bqm.move_forward()
    # Get position
    print(motor_bqm.get_pos())    
    # Reset motor
    motor_bqm.stop_and_reset_motor()
    # Get energized state of motor
    print(motor_bqm.get_motor_state())

if __name__ == "__main__":
    main()
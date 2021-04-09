import time

import helper_profiler
import motor_ball_feed
import motor_ball_queue
import motor_flywheel_bottom
import motor_flywheel_top
import motor_pitch
import motor_yaw


class DrillSessionHandler:
    """This class handles all actual automated or manual drill execution, including sending instructions to motors appropriately
    """

    def __init__(self, drill_name=None, goalie_name=None):
        """Initializes the drill session handler

        Args:
            drill_name ([str], optional): Name of the drill to be executed for an automated session. If manual training session, defaults to None.
            goalie_name ([str], optional): Goalie's name for an automated session. If manual training, defaults to None.
        """
        self.drill_name = drill_name
        self.goalie_name = goalie_name

        # Load the drill process
        self.profiler = helper_profiler.Profiler()
        self.drill_info = self.profiler.get_profile_info(self.drill_name)

        # Initialize all motors
        self.bfm = motor_ball_feed.MotorBallFeed()
        self.bqm = motor_ball_queue.MotorBallQueue()
        self.fmt = motor_flywheel_top.MotorFlywheelTop()
        self.fmb = motor_flywheel_bottom.MotorFlywheelBottom()
        self.pm = motor_pitch.MotorPitch()
        self.ym = motor_yaw.MotorYaw()

        # How long it takes (in seconds) for the ball to catch onto the flywheels, in which case the BFM moves back
        self.bfm_wait = 1

    def start_drill(self):
        """Executes all the steps required to start an automated or manual drill, such as enabling the motor
        NOTE: Possibly store all possible pitch and yaw angle requirements from the current position here. This would expedite the shooting process
        """

        # Enable all motors
        # NOTE: Order matters!
        self.fmt.energize_motor()
        self.fmb.energize_motor()
        self.ym.energize_motor()
        self.pm.energize_motor()
        self.bfm.energize_motor()
        # NOTE: BQM may need to be enabled right before running the drill
        self.bqm.energize_motor()

    def run_automated_drill(self):
        """Runs an automated drill session
        """
        for each_ball_info in self.drill_info.values():
            self.run_manual_drill(
                shot_loc=each_ball_info[0], ball_speed=each_ball_info[1])

    def run_manual_drill(self, shot_loc, ball_speed):
        """Runs a manual drill session

        Args:
            shot_loc ([str]): Shot location
            ball_speed ([int]): Ball speed
        """
        # 1. Drop a ball by moving the ball queue motor
        self.bqm.move_queue()

        # 2. Adjust pitch and yaw motor appropriately
        # 2.1: Get which goal area it the drill shot needs to happen in terms of angle that pitch and yaw need to be adjusted
        # NOTE: This substep will call the trajectory class
        # 2.2: Set pitch and yaw at that angle
        self.ym.set_angle("")
        self.pm.set_angle("")

        # 3. Set the speed of both flywheels
        self.set_flywheel_speeds(ball_speed)

        # 4. Shoot the ball
        self.bfm_shoot_movement()

    def bfm_shoot_movement(self):
        """Ball feeding mechanism movement
        """

        # Move the feed motor forward, wait for it to get caught into the flywheels, then come back
        self.bfm.move_forward()
        time.sleep(self.bfm_wait)
        self.bfm.move_backward()

    def set_flywheel_speeds(self, speed):
        """Top and Bottom Flywheels speed setter

        Args:
            speed ([int]): Target speed for flywheels
        """

        # Set the flywheel speeds
        self.fmt.set_speed(speed)
        self.fmb.set_speed(speed)

    def stop_drill(self):
        """Executes all steps required when drill has been stopped or has ended
        """
        # Save the drill profile to the goalie's name
        if self.goalie_name is not None:
            self.profiler.save_drill_to_goalie_profile(
                self.goalie_name, self.drill_name)

        # Stop and reset all motors
        self.bfm.stop_and_reset_motor()
        self.bqm.stop_and_reset_motor()
        self.fmt.stop_and_reset_motor()
        self.fmb.stop_and_reset_motor()
        self.pm.stop_and_reset_motor()
        self.ym.stop_and_reset_motor()


def main():
    pass


if __name__ == "__main__":
    main()

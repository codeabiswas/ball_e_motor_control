try:
    import sys
    from pathlib import Path
    sys.path.append(
        "{}/Developer/ball_e_image_processing/src".format(Path.home()))
    import trajectory_algorithm
except:
    print("Import failed")
finally:
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

    def __init__(self, distance_from_goal, drill_name=None, goalie_name=None):
        """Initializes the drill session handler

        Args:
            distance_from_goal ([float]): The distance from Ball-E to the goal in feet
            drill_name ([str], optional): Name of the drill to be executed for an automated session. If manual training session, defaults to None.
            goalie_name ([str], optional): Goalie's name for an automated session. If manual training, defaults to None.
        """
        self.drill_name = drill_name
        self.goalie_name = goalie_name
        self.distance_from_goal = distance_from_goal

        # The first ball (index 0) means ball queue needs to rotate 1/36. The rest will rotate 1/18.
        self.first_ball = True

        # Load the drill process
        self.profiler = helper_profiler.Profiler()
        self.drill_info = self.profiler.get_profile_info(self.drill_name)

        # Initialize Trajectory Algorithm Helper
        self.trajectory_algo = trajectory_algorithm.TrajectoryAlgorithm(
            self.distance_from_goal)

        # Initialize all motors
        self.bfm = motor_ball_feed.MotorBallFeed()
        self.bqm = motor_ball_queue.MotorBallQueue()
        self.fmt = motor_flywheel_top.MotorFlywheelTop()
        self.fmb = motor_flywheel_bottom.MotorFlywheelBottom()
        self.pm = motor_pitch.MotorPitch()
        self.ym = motor_yaw.MotorYaw()

    def start_drill(self):
        """Executes all the steps required to start an automated or manual drill, such as enabling the motor
        NOTE: Possibly store all possible pitch and yaw angle requirements from the current position here. This would expedite the shooting process
        """

        # Enable all motors
        # NOTE 1: Order matters!
        # NOTE 2: BFM not energized since it will cause motor to move
        self.fmt.energize_motor()
        self.fmb.energize_motor()
        self.ym.energize_motor()
        self.pm.energize_motor()
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
        # 1. Adjust pitch and yaw motor appropriately
        # 1.1: Get which goal area it the drill shot needs to happen in terms of angle that pitch and yaw need to be adjusted
        yaw_angle, pitch_angle = self.get_shot_angles(shot_loc)
        # 1.2: Set pitch and yaw at that angle
        self.ym.set_angle(yaw_angle)
        self.pm.set_angle(pitch_angle)

        # 2. Set the speed of both flywheels
        self.set_flywheel_speeds(ball_speed)

        # 3. Drop a ball by moving the ball queue motor
        self.bqm_move_queue()

        # 4. Shoot the ball
        self.bfm_shoot_movement()

    def get_shot_angles(self, shot_loc):
        """Returns the shot angles required for pitch and yaw from set distance

        Args:
            shot_loc (string): Shot location on the lacrosse goal (TL, TM, TR, CL, CM, CR, BL, BM, BR)

        Returns:
            [tuple]: Yaw degree, Pitch degree
        """
        return (self.trajectory_algo.calc_yaw(shot_loc), self.trajectory_algo.calc_pitch(shot_loc))

    def bqm_move_queue(self):
        """Rotates the ball queue so that a ball can drop into the ball feed
        """
        if self.first_ball == 0:
            self.bqm.turn_once_half()
        else:
            self.bqm.turn_once_full()

        self.first_ball += 1

    def bfm_shoot_movement(self):
        """Ball feeding mechanism movement
        """

        # TODO: Wait for some time based on ROF

        # Move the feed motor forward, wait for it to get caught into the flywheels, then come back
        #Currently waiting 1.1 seconds each direction of the bfm movement
        #2.2 seconds total
        #So wait (ROF-2.2)/2 in each direction and hope that the LAX ball has fallen by then


        time.sleep((ROF-2.2)/2)
        self.bfm.move_forward()
        self.bfm.move_backward()
        time.sleep((ROF-2.2)/2)

        # TODO: Wait for some time based on ROF

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

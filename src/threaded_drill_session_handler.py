try:
    import sys
    from pathlib import Path
    sys.path.append(
        "{}/Developer/ball_e_image_processing/src".format(Path.home()))
    import trajectory_algorithm
except:
    print("Import failed")
finally:
    import csv
    import datetime
    import time

    from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot

    import helper_profiler
    import motor_ball_feed_vel
    import motor_ball_queue
    import motor_ball_queue_updated
    import motor_flywheel_bottom
    import motor_flywheel_top
    import motor_pitch
    import motor_yaw


class ThreadedDrillSessionHandler(QThread):
    """This class handles all actual automated or manual drill execution, including sending instructions to motors appropriately
    """
    run_drill_signal = pyqtSignal(bool)
    update_ball_num_signal = pyqtSignal(bool)

    def __init__(self, distance_from_goal, drill_name=None, goalie_name=None):
        """Initializes the drill session handler

        Args:
            distance_from_goal ([float]): The distance from Ball-E to the goal in feet
            drill_name ([str], optional): Name of the drill to be executed for an automated session. If manual training session, defaults to None.
            goalie_name ([str], optional): Goalie's name for an automated session. If manual training, defaults to None.
        """
        super().__init__()
        self.run_drill = True

        self.drill_name = drill_name
        self.goalie_name = goalie_name
        self.distance_from_goal = distance_from_goal

        # The first ball (index 0) means ball queue needs to rotate 1/36. The rest will rotate 1/18.
        self.first_ball = True

        if self.drill_name is not None:
            # Load the drill process
            # self.profiler = helper_profiler.Profiler()
            # self.drill_info = self.profiler.get_profile_info(self.drill_name)
            self.drill_info = self.get_profile_info()

            self.rof = int(self.drill_info['1'][2])

        # Initialize Trajectory Algorithm Helper
        self.trajectory_algo = trajectory_algorithm.TrajectoryAlgorithm(
            self.distance_from_goal)

        # Initialize all motors
        self.bfm = motor_ball_feed_vel.MotorBallFeed()
        self.bqm = motor_ball_queue_updated.MotorBallQueue()
        # self.bqm = motor_ball_queue.MotorBallQueue()
        self.fmt = motor_flywheel_top.MotorFlywheelTop()
        self.fmb = motor_flywheel_bottom.MotorFlywheelBottom()
        self.pm = motor_pitch.MotorPitch()
        self.ym = motor_yaw.MotorYaw()

        # Stores previous shot location
        self.prev_shot_loc = "CM"

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

        # Enabling motors takes time
        time.sleep(2)

    def run_automated_drill(self):
        """Runs an automated drill session
        """
        for each_ball_info in self.drill_info.values():
            self.run_manual_drill(
                shot_loc=each_ball_info[0], ball_speed=int(each_ball_info[1]))
            self.update_ball_num_signal.emit(True)
        self.stop_drill()

    def run_manual_drill(self, shot_loc, ball_speed):
        """Runs a manual drill session

        Args:
            shot_loc ([str]): Shot location
            ball_speed ([int]): Ball speed
        """
        if self.run_drill:
            print("\n\nShot location: {}".format(shot_loc))
            # 1. Adjust pitch and yaw motor appropriately
            # 1.1: Get which goal area it the drill shot needs to happen in terms of angle that pitch and yaw need to be adjusted
            yaw_angle, pitch_angle = self.get_shot_angles(shot_loc)
            print("curr yaw angle: {}".format(yaw_angle))
            print("curr pitch angle: {}".format(pitch_angle))
            prev_yaw_angle, prev_pitch_angle = self.get_shot_angles(
                self.prev_shot_loc)
            print("prev yaw angle: {}".format(prev_yaw_angle))
            print("prev pitch angle: {}".format(prev_pitch_angle))
            target_yaw_angle = yaw_angle - prev_yaw_angle
            target_pitch_angle = pitch_angle - prev_pitch_angle
            print("curr-prev yaw angle: {}".format(target_yaw_angle))
            print("curr-prev pitch angle: {}\n".format(target_pitch_angle))

            # 1.2: Set pitch and yaw at that angle
            if target_yaw_angle < 0:
                self.ym.move_left(target_yaw_angle)
            elif target_yaw_angle > 0:
                self.ym.move_right(target_yaw_angle)
            else:
                pass
            if target_pitch_angle < 0:
                self.pm.pitch_down(target_pitch_angle)
            elif target_pitch_angle > 0:
                self.pm.pitch_up(target_pitch_angle)
            else:
                pass

            # 2. Set the speed of both flywheels
            self.set_flywheel_speeds(ball_speed)

            # 3. Drop a ball by moving the ball queue motor
            self.bqm_move_queue()

            # 4. Shoot the ball
            self.bfm_shoot_movement()

            # Update shot location for relative test
            self.prev_shot_loc = shot_loc

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
        # if self.first_ball == 0:
        #     self.bqm.turn_once_half()
        # else:
        #     self.bqm.turn_once_full()

        # self.first_ball += 1
        self.bqm.turn_once()

    def bfm_shoot_movement(self):
        """Ball feeding mechanism movement
        """

        # TODO: Wait for some time based on ROF

        # Move the feed motor forward, wait for it to get caught into the flywheels, then come back
        # Currently waiting 1.1 seconds each direction of the bfm movement
        # 2.2 seconds total
        # So wait (ROF-2.2)/2 in each direction and hope that the LAX ball has fallen by then

        if self.drill_name is not None:
            time.sleep((self.rof-2.2)/2)
        self.bfm.move_forward()
        self.bfm.move_backward()
        if self.drill_name is not None:
            time.sleep((self.rof-2.2)/2)

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
        self.run_drill = False
        self.run_drill_signal.emit(False)

        # Save the drill profile to the goalie's name
        if self.goalie_name is not None:
            # self.profiler.save_drill_to_goalie_profile(
            #     self.goalie_name, self.drill_name)
            self.save_drill_to_goalie_profile()

        # Stop and reset all motors
        self.bfm.stop_and_reset_motor()
        self.bqm.stop_and_reset_motor()
        self.fmt.stop_and_reset_motor()
        self.fmb.stop_and_reset_motor()
        self.ym.stop_and_reset_motor()
        self.pm.stop_and_reset_motor()

        self.wait()

    def save_drill_to_goalie_profile(self):
        goalie_path = str(Path.home())+"/Documents/ball_e_profiles/goalie_profiles/{goalie_name}/{goalie_name}.csv".format(
            goalie_name=self.goalie_name)
        with open(goalie_path, 'a+', newline='') as file:
            csv_writer = csv.writer(file, delimiter=",")
            # Row written as "Drill Name, MM/DD/YYYY"
            drill_info = ["{}".format(self.drill_name.replace("_", " ").title()), "{}".format(
                datetime.datetime.today().strftime("%m/%d/%Y"))]
            csv_writer.writerow(drill_info)

    def get_profile_info(self):
        drill_path = str(Path.home())+"/Documents/ball_e_profiles/drill_profiles/{drill_name}/{drill_name}.csv".format(
            drill_name=self.drill_name)
        with open(drill_path) as file:
            csv_reader = csv.reader(file, delimiter=',')
            row_count = 0
            info_dict = dict()
            for row in csv_reader:
                if row_count == 0:
                    row_count += 1
                else:
                    info_dict[row[0]] = [row[1], row[2], row[3]]
                    row_count += 1

        return info_dict


def run_manual_session():
    manual_session = ThreadedDrillSessionHandler(10)
    print("Enabling all motors...")
    manual_session.start_drill()
    time.sleep(2)
    print("Shoot at TR with speed 30...")
    manual_session.run_manual_drill(shot_loc="TR", ball_speed=30)
    time.sleep(2)
    print("Shoot at BL with speed 30...")
    manual_session.run_manual_drill(shot_loc="BL", ball_speed=30)
    time.sleep(2)
    print("Shoot at CM with speed 65...")
    manual_session.run_manual_drill(shot_loc="CM", ball_speed=65)
    time.sleep(2)
    # print("Shoot at TL with speed 30...")
    # manual_session.run_manual_drill(shot_loc="TL", ball_speed=30)
    # time.sleep(5)
    # print("Shoot at BR with speed 30...")
    # manual_session.run_manual_drill(shot_loc="TL", ball_speed=30)
    # time.sleep(5)
    # print("Shoot at BM with speed 100...")
    # manual_session.run_manual_drill(shot_loc="BM", ball_speed=100)
    # time.sleep(5)
    manual_session.stop_drill()


def run_automated_session():
    automated_session = ThreadedDrillSessionHandler(10, drill_name="t_drill")
    automated_session.start_drill()
    automated_session.run_automated_drill()
    # automated_session.stop_drill()


def main():
    # run_manual_session()
    run_automated_session()


if __name__ == "__main__":
    main()

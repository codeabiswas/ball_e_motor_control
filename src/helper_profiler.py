import csv
import datetime
import os
from pathlib import Path


class Profiler:

    def save_drill_to_goalie_profile(self, goalie_name, drill_name):
        goalie_path = str(Path.home())+"/Documents/ball_e_profiles/goalie_profiles/{goalie_name}/{goalie_name}.csv".format(
            goalie_name=goalie_name)
        with open(goalie_path, 'a+', newline='') as file:
            csv_writer = csv.writer(file, delimiter=",")
            # Row written as "Drill Name, MM/DD/YYYY"
            drill_info = ["{}".format(drill_name.replace("_", " ").title()), "{}".format(
                datetime.datetime.today().strftime("%m/%d/%Y"))]
            csv_writer.writerow(drill_info)

    @staticmethod
    def get_profile_info(drill_name):
        drill_path = str(Path.home())+"/Documents/ball_e_profiles/drill_profiles/{drill_name}/{drill_name}.csv".format(
            drill_name=drill_name)
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


def main():
    some_profiler = Profiler()
    some_profiler.save_drill_to_goalie_profile("andrei_biswas", "drill_a")
    drill_dict = some_profiler.get_profile_info("drill_a")
    # Get ROF
    print(drill_dict['1'][2])


if __name__ == "__main__":
    main()

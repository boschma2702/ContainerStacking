import os

from main.util import sub_folder_file, sub_folder


class FileWriter:

    FILE_INSTANCE_RESULTS = "results.csv"
    FILE_RESHUFFLES = "reshuffles.csv"
    FILE_INIT_VALUES = "init_values.csv"
    FILE_WEIGHTS = "weights.txt"
    FILE_PROGRESS = "progress.txt"

    def __init__(self, name: str, instance_number: int, terminal_type: str, adp_setting):
        self.name = adp_setting.get_name(name)
        self.instance_number = instance_number
        self.terminal_type = terminal_type

        self.root_folder_path = sub_folder(["evaluation", self.name])
        self.instance_folder_path = sub_folder(["evaluation", self.name, "instance#{:02d}".format(instance_number)])
        self.final_result_folder = sub_folder(["evaluation", "final"])

        self.final_file_name = "t{}-{}.csv".format(terminal_type, self.name)
        self.instance_file = "instance#{:02d}.csv".format(instance_number)

        # make sure both folders exist
        self.check_folder_exist(self.final_result_folder)
        self.check_folder_exist(self.root_folder_path)
        self.check_folder_exist(self.instance_folder_path)

    def check_folder_exist(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def __write(self, path: str, filename: str, contents: str):
        file = open(sub_folder_file(path, filename), "a+")
        file.write(contents + "\n")
        file.close()

    def write_to_instance_folder(self, file: str, contents: str):
        self.__write(self.instance_folder_path, "t{}-{}".format(self.terminal_type, file), contents)

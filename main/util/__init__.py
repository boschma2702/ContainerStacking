import os
from typing import List, Union

from definitions import EXPORT_DIR, ROOT_DIR


def sub_folder(subfolders: Union[str, List[str]]):
    if type(subfolders) is str:
        return os.path.join(ROOT_DIR, *[subfolders])
    if type(subfolders) is List or type(subfolders) is list:
        return os.path.join(ROOT_DIR, *subfolders)
    else:
        raise RuntimeError("Unknown type: {}".format(type(subfolders)))


def sub_folder_file(subfolders: Union[str, List[str]], filename: str):
    if type(subfolders) is str:
        return os.path.join(ROOT_DIR, *[subfolders, filename])
    if type(subfolders) is List or type(subfolders) is list:
        return os.path.join(ROOT_DIR, *(subfolders + [filename]))
    else:
        raise RuntimeError("Unknown type: {}".format(type(subfolders)))


def writeToFile(name, string_contents, extension="csv", base_path=EXPORT_DIR):
    filename = "{}.{}".format(name, extension)
    path = os.path.join(base_path, filename)
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.mkdir(dir)

    f = open(path, "w")
    f.write(string_contents)
    f.close()


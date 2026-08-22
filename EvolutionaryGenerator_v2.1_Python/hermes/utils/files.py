"""Translation of ``mx.tec.hermes.utils.Files``."""

import os
import sys


def load(file_name: str) -> str:
    """Reads a text file and returns a string with its contents.

    :param file_name: The name of the text file to be read.
    :return: A string with the contents of the text file.
    """
    try:
        # ``newline=""`` disables the universal newlines translation so the string
        # returned is byte for byte the one Java's FileReader would produce.
        with open(file_name, "r", newline="") as file:
            return file.read()
    except OSError as e:
        print("An error occurred while attempting to read the file '" + file_name + "'.")
        print("Exception: " + str(e))
        print("The system will halt.")
        sys.exit(1)
    return None


def save(string: str, file_name: str) -> None:
    """Saves a string to a text file.

    :param string: The string to be saved.
    :param file_name: The name of the file where the string will be saved.
    """
    try:
        # ``newline=""`` keeps the \r\n sequences written by the callers untouched,
        # exactly as Java's FileWriter does.
        with open(file_name, "w", newline="") as file:
            file.write(string)
    except OSError as e:
        print('An error occurred while attempting to save the file "' + file_name + '".')
        print("Exception: " + str(e))
        print("The system will halt.")
        sys.exit(1)


def list_files(folder_name: str) -> list:
    """Returns the names of all the files in the folder provided.

    :param folder_name: The folder where the files are stored.
    :return: The names of all the files in the folder provided.
    """
    if not os.path.exists(folder_name) or not os.path.isdir(folder_name):
        print('The path "' + folder_name + '" is not a valid directory.', file=sys.stderr)
        print("The system will halt.", file=sys.stderr)
        sys.exit(1)
    return sorted(os.listdir(folder_name))


class Files:
    """Provides the methods to save and load text files.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: José Carlos Ortiz Bayliss (jcobayliss@gmail.com)
    :original version: 1.0
    """

    load = staticmethod(load)
    save = staticmethod(save)
    list_files = staticmethod(list_files)

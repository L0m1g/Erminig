import os
import configparser


class Config:
    """
    Class to interact with config files

    Attributes
    ----------
    path : str
        config file path

    Methods
    -------
    def get(self, section, key)
        return a configuration value

    def set(self, section, key, value):
        record a value in a section
    """

    def __init__(self, path):
        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    def get(self, section, key):
        """
        Return a configuration value

        Parameters
        ----------
        section : str
            Section of the config file
        key : str
            Key to which to retrieve a value
        """
        return self.config[section][key]

    def set(self, section, key, value) -> None:
        """
        Set a section, key, value in config file

        Parameters:
        section : str
            Section
        key : str
            Key
        value : str
            Value
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][key] = value

        with open(self.path, "w") as configfile:
            self.config.write(configfile)

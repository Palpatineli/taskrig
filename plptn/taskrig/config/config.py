"""Provide Path information and experiment design parameters
by Keji Li 10/26/2015 mail@keji.li in Sur lab, MIT PILM"""
import json
import platform
import time
from collections import MutableMapping
from os import path, makedirs, access, W_OK

CONFIG_PATH = path.join(path.dirname(path.dirname(__file__)), 'config')


def deep_update(x: dict, y: dict) -> dict:
    """merges y into x
    Args:
        x: the dictionary to be updated
        y: update from y"""
    for key in y:
        if key in x and isinstance(x[key], dict) and isinstance(y[key], dict):
            deep_update(x[key], y[key])
        x[key] = y[key]
    return x


def device_config():
    device_dict = json.load(open(path.join(CONFIG_PATH, 'device', 'index.json'), 'r'))
    device_name = device_dict[platform.node()]
    config = json.load(open(path.join(CONFIG_PATH, 'device', device_name + '.json'), 'r'))
    return config


class Logger(object):
    def __init__(self):
        current_time = time.localtime()
        self.folder = path.expanduser("~/psyStimLogs/")
        self.today_folder = path.join(self.folder, time.strftime("%Y-%m-%d", current_time))
        self.path = path.join(self.today_folder, time.strftime("%H%M%S", current_time) + ".log")

    def __enter__(self):
        if not path.exists(self.folder):
            makedirs(self.folder)
        if not path.exists(self.today_folder):
            makedirs(self.today_folder)
        if not access(self.today_folder, W_OK):
            raise IOError("{0} folder is not writable "
                          "by stimulus logger.".format(self.today_folder))
        self.config = None
        self.timestamps = list()
        self.sequence = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del exc_type, exc_val, exc_tb
        data = {'timestamps': self.timestamps}
        if self.config is not None:
            data['config'] = self.config
        if self.sequence is not None:
            data['sequence'] = self.sequence
        json.dump(data, open(self.path, 'w'), indent=4, separators=(',', ': '))


class Design(MutableMapping):
    """only direct writing of item is persistent. writing elements of items is not.
    """
    is_modified = False
    default_str = "default"

    def __init__(self, design_type):
        self.design_type = design_type
        with open(path.join(CONFIG_PATH, 'design', design_type + '.json'), 'r') as config_file:
            temp_dict = json.load(config_file)
        set_hierarchy = list()
        set_hierarchy.append(temp_dict)
        while 'base' in temp_dict:
            with open(path.join(CONFIG_PATH, 'design', temp_dict['base'] + '.json'),
                      'r') as config_file:
                temp_dict = json.load(config_file)
            set_hierarchy.append(temp_dict)
        set_hierarchy.reverse()
        combined_dict = set_hierarchy[0].copy()
        for temp_dict in set_hierarchy[1:]:
            deep_update(combined_dict, temp_dict)
        self.read_dict = combined_dict
        self.write_dict = set_hierarchy[-1]

    def __del__(self):
        if self.is_modified:
            json.dump(self.write_dict,
                      open(path.join(CONFIG_PATH, 'design', self.design_type + '.json'), 'w'),
                      sort_keys=True, indent=4, separators=(',', ': '))

    def __contains__(self, item):
        return self.read_dict.__contains__(item)

    def __getitem__(self, key):
        return self.read_dict[key]

    def __setitem__(self, key, value):
        self.write_dict[key] = value
        self.read_dict[key] = value
        self.is_modified = True

    def __delitem__(self, key):
        raise NotImplementedError

    def __len__(self):
        return self.read_dict.__len__()

    def __iter__(self):
        return self.read_dict.__iter__()

    def __str__(self):
        return ''.join(['{}: {}\n'.format(key, str(value)) for key, value in self.items()
                        if key not in ('base', 'user_changeable')])

    def to_dict(self):
        return {key: value for key, value in self.items() if key not in ('base', 'user_changeable')}

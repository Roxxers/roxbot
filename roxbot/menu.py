# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2017-2018 Roxanne Gibson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class Menu:

    __slots__ = ["name", "params", "formatted_params", "title", "content"]

    def __init__(self, name,  *params, settings=None):
        self.name = name
        self.params = list(params).append("Exit")
        if settings:
            self.formatted_params = self._parse_params(settings, self.name)
        else:
            self.formatted_params = self.params
        self.title = "'Roxbot Settings: {}'\n".format(self.name)
        self.content = self._format_content(self.title, self.formatted_params, "```python", "```")

    @staticmethod
    def _format_content(title, params, prefix="", suffix=""):
        separator = "—————————————————————————————"
        choices = "\n"
        for x, setting in enumerate(params):
            if setting == "Exit":
                choices += "[0] Exit\n"
            elif setting != "convert":
                if setting != [*params][x]:  # Just in case params is dict_keys, we make a new list.
                    choices += "[{}] {}\n".format(x + 1, setting)
                else:
                    choices += "[{}] Edit '{}'\n".format(x+1, setting)
        return prefix + title + separator + choices + suffix

    @staticmethod
    def _parse_params(settings, name):
        params = [*settings.keys()]
        params_copy = settings.copy().keys()
        for param in params_copy:
            if settings["convert"].get(param) == "bool":
                # Enable/Disable Parse
                if param == "enabled":
                    options = ["Enable '{}'".format(name), "Disable '{}'".format(name)]
                else:
                    options = ["Enable '{}'".format(param), "Disable '{}'".format(param)]
                params.remove(param)
                params = [*options, *params]
            elif isinstance(settings.get(param), list):
                # Add and Remove Parse
                options = ["Add {}".format(param), "Remove {}".format(param)]
                params.remove(param)
                params = [*params, *options]
            elif isinstance(settings.get(param), (int, str)):
                # Set parse
                options = "Set {}".format(param)
                params.remove(param)
                params = [*params, options]
        return params

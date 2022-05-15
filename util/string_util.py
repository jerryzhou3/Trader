# ！/usr/bin/env python
# encoding: utf-8
"""
@Author:
@File: string_util.py
@Time: 2022/5/14 21:01
@Describe:
"""


class StringBuilder:
    def __init__(self):
        self.string = ""

    def append(self, *args, sep=" ", end: str = "\n"):
        self.string += sep.join([str(arg) for arg in args]) + end

    def to_string(self):
        return self.string

    def clear(self):
        self.string = ""

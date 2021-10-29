#!/usr/bin/env python3

"""
Common testable functions for strings
"""


def multi_replace_curry(replacements):
    def multi_replace(string):
        new_string = string
        for old, new in replacements:
            new_string = new_string.replace(old, new)
        return new_string

    return multi_replace

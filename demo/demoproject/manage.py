#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Command line for Django."""
import os
import sys

from django.core.management import execute_from_command_line


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          f"{__package__}.settings")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

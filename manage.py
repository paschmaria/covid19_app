#!/usr/bin/env python
import os
import sys

from dotenv import find_dotenv, load_dotenv

if __name__ == "__main__":
    try:
        load_dotenv(find_dotenv(
                        filename='env/local.env',
                        raise_error_if_not_found=True
                    ))
    except OSError:
        load_dotenv(find_dotenv(filename='env/prod.env'))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

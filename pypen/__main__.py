import sys
import argparse
import time
from os import path, getcwd
from importlib import util as import_util

from pypen.settings import settings

import pygame

display = pygame.display.set_mode((settings.width, settings.height),
                                  pygame.SRCALPHA) if not settings._is_executing_with_python else None

def cli():
    try:
        main_argument_parser = argparse.ArgumentParser(
            description="The PyPen CLI for managing PyPen Sketches", prog="pypen")

        sub_argument_parsers = main_argument_parser.add_subparsers(help="'pypen run' for running sketches and 'pypen init' to create a new one.")

        run_parser = sub_argument_parsers.add_parser("run", description="Command used to run sketches.")

        run_parser.add_argument(
            "filename", help="The name/path to the file that contains your PyPen Sketch.")

        run_parser.add_argument("-f", "--fullscreen", action="store_true")

        run_parser.add_argument(
            "--timeout", help="Timeout in seconds. Window will close once done.", type=float, required=False, default=0.0)
        
        init_parser = sub_argument_parsers.add_parser("init", description="Optional command to create a default PyPen file with imports and default functions.")

        init_parser.add_argument("filename", help="The name/path to the to-be-created PyPen (with or without .py extension)", default="new_pypen.py")

        arguments = main_argument_parser.parse_args()

        if len(sys.argv) == 1:
            main_argument_parser.print_help(sys.stderr)
            sys.exit(0)

        main(arguments)
    except argparse.ArgumentError as error:
        print(str(error))
        sys.exit(2)


def main(arguments):
    try:
        file_path = path.join(getcwd(), arguments.filename)
        spec = import_util.spec_from_file_location("", file_path)
        user_sketch = import_util.module_from_spec(spec)
        spec.loader.exec_module(user_sketch)
    except FileNotFoundError:
        print()
        print(f"Hmm, PyPen can't find '{arguments.filename}'.")
        print("Are you sure that's the right path?")
        print()
        sys.exit(1)

    try:
        user_sketch.TIME
        user_sketch.T
        user_sketch.rectangle
        user_sketch.PI
    except AttributeError:
        print()
        print(f"It seems like you're not importing PyPen to your sketch '{arguments.filename}'")
        print("Import it by writing 'from pypen import *' at the very top!")
        print()
        sys.exit(1)

    try:
        user_sketch.start
    except AttributeError:
        settings._user_has_start = False

    try:
        user_sketch.update
    except AttributeError:
        settings._user_has_update = False

    if not settings._user_has_start and not settings._user_has_update:
        print()
        print(
            f"Your PyPen sketch '{arguments.filename}' appears to have neither a start() nor an update() function.")
        print("Try to add at least one of those and run again!")
        print()
        sys.exit(1)

    def start():
        user_sketch.start()
        update()

    def update(passed_time=0, delta_time=0, frame_count=0):
        user_sketch.TIME = user_sketch.T = passed_time
        user_sketch.DELTA_TIME = user_sketch.DT = delta_time
        user_sketch.FRAME = user_sketch.F = frame_count

        user_sketch.update()

    pygame.init()
    pygame.display.set_caption(f"PyPen | {arguments.filename}")

    if settings._user_has_start:
        start()

    pygame.display.flip()
    clock = pygame.time.Clock()

    is_running = True
    passed_time = frame_count = 0

    while is_running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_running = False

        delta_time = clock.tick(settings.fps if settings.fps > 0 else 1)/1000
        passed_time += delta_time
        frame_count += 1

        if arguments.timeout > 0:
            if passed_time > arguments.timeout:
                is_running = False

        if settings._user_has_update:
            update(passed_time, delta_time, frame_count)

        pygame.display.flip()


if __name__ == "__main__":
    cli()

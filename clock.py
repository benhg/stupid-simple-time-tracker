#!/usr/local/bin/python3

import argparse
import json
import sys
import datetime
import time
import os
from dateutil.relativedelta import relativedelta

PUNCH_FILE = "/Users/ben/clock_log.json"
TIME_FORMAT = "%m/%d/%Y, %H:%M:%S"
"""
Schema:
[
  {
    "clock_in" : TIMESTAMP,
    "clock_out": TIMESTAMP,
    "notes": "Optional String"
  },
  {
    "clock_in" : TIMESTAMP,
    "clock_out": TIMESTAMP
  },
]

"""


def create_new_entry():
    entry = {"clock_in": time.time(), "clock_out": -1}
    return entry


def record_action(args):
    current_log = json.load(open(PUNCH_FILE))
    current_log = sorted(current_log, key=lambda x: x.get("clock_in", -1))
    if args.clock_in:
        if (len(current_log) > 0) and (current_log[-1]["clock_out"] == -1):
            print("ERROR: Currently clocked in.")
            sys.exit(-1)
        # Create new entry with -1 as clock out time
        new_log = create_new_entry()
        current_log.append(new_log)
    elif args.clock_out:
        if current_log[-1]["clock_out"] != -1:
            print("ERROR: Already clocked out")
            sys.exit(-1)
        current_log[-1]["clock_out"] = time.time()
    else:
        print("ERROR: Unexpected command")
        sys.exit(-1)

    if (args.notes):    
        current_log[-1]["notes"] = args.notes

    json.dump(current_log, open(PUNCH_FILE, "w"))
    return


def readable_delta(time_in, time_out):
    attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
    delta = relativedelta(time_out, time_in)
    return [
        '%d %s' %
        (getattr(delta, attr), attr if getattr(delta, attr) > 1 else attr[:-1])
        for attr in attrs if getattr(delta, attr)
    ]


def view_history(view_opts):
    data = json.load(open(PUNCH_FILE))
    if "raw" in view_opts:
        print("==========RAW HISTORY:==========")
        print(json.dumps(data, indent=2))
        print("========END RAW HISTORY:========")
    if "human" in view_opts:
        print("========HUMAN HISTORY:========")
        data_2 = []
        for d in data:
            time_in = datetime.datetime.fromtimestamp(d["clock_in"])
            time_out = datetime.datetime.fromtimestamp(d["clock_out"])
            entry = {
                "clock_in": time_in.strftime(TIME_FORMAT),
                "clock_out": time_out.strftime(TIME_FORMAT),
                "notes": d.get("notes", "")
            }
            data_2.append(entry)
        print(json.dumps(data_2, indent=2))
        print("========END HUMAN HISTORY:========")
    if "parsed" in view_opts:
        print("========PARSED HISTORY:========")
        data_2 = []
        for d in data:
            time_in = datetime.datetime.fromtimestamp(d["clock_in"])
            time_out = datetime.datetime.fromtimestamp(d["clock_out"])
            entry = {
                "clock_in": time_in.strftime(TIME_FORMAT),
                "clock_out": time_out.strftime(TIME_FORMAT),
                "total_time": " ".join(readable_delta(time_in, time_out)),
                "notes": d.get("notes", "")
            }
            data_2.append(entry)
        print(json.dumps(data_2, indent=2))
        print("========END PARSED HISTORY:========")
    if "total_time" in view_opts:
        print("Show the total amount of time in hours")
    if "summary" in view_opts:
        print("Show the time broken down per day")
    if "summary_week" in view_opts:
        print("Show the time broken down per week")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--clock-in",
                        "-i",
                        help="clock in",
                        action="store_true",
                        default=False)
    parser.add_argument("--clock-out",
                        "-o",
                        help="clock out",
                        action="store_true",
                        default=False)
    parser.add_argument("--reset",
                        "-r",
                        help="erase history",
                        action="store_true",
                        default=False)
    parser.add_argument("--view",
                        "-v",
                        required=False,
                        help="View history",
                        type=str,
                        nargs="+",
                        default=[],
                        choices=[
                            "raw", "human", "parsed", "total_time", "summary",
                            "summary_week"
                        ])
    parser.add_argument("--notes",
                        "-n",
                        required=False,
                        help="Add notes to a punch in or out",
                        type=str,
                        default="")
    args = parser.parse_args()

    if not os.path.exists(PUNCH_FILE) or args.reset:
        with open(PUNCH_FILE, "w") as fh:
            fh.write("[]")
    if not os.path.isfile(PUNCH_FILE):
        print("ERROR: Save file not found.")
        sys.exit(-1)

    if args.clock_in and args.clock_out:
        print("ERROR: Cannot clock both in and out")
        sys.exit(-1)

    if args.clock_in or args.clock_out:
        record_action(args)
    else:
        view_history(args.view)
    sys.exit(0)

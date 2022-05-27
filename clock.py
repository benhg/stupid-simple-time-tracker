#!/usr/local/bin/python3

import argparse
import json
import sys
import datetime
import time

PUNCH_FILE = "/Users/ben/clock_log.json"

"""
Schema:
[
  {
	"clock_in" : TIMESTAMP,
	"clock_out": TIMESTAMP
  },
  {
	"clock_in" : TIMESTAMP,
	"clock_out": TIMESTAMP
  },
]

"""

def create_new_entry():
	entry = {"clock_in": time.time(),
	         "clock_out": -1}
	return entry


def record_action(args: Namespace):
	current_log = json.load(open(PUNCH_FILE))
	if args.clock_in:
		# Create new entry with -1 as clock out time
		new_log = create_new_entry()
		current_log.append(new_log)
	else if args.clock_out:
		current_log = sorted(current_log, key=lambda x: x.get("clock_in", -1))
		current_log[-1]["clock_out"] = time.time()
	else:
		print("ERROR: Unexpected command")
		sys.exit(-1)

	json.dump(open(PUNCH_FILE, "w"))
	return

def view_history():
	with open(PUNCH_FILE) as fh:
		print(json.dump(fh, indent=2))


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_args("--clock-in", "-i", help="clock in", action="store_true", default=False)
	parser.add_args("--clock-out", "-o", help="clock out", action="store_true", default=False)
	parser.add_args("--view", "-v", help="view history", action="store_true", default=False)
	args = parser.parse_args()

	if args.clock_in and args.clock_out:
		print("ERROR: Cannot clock both in and out")
		sys.exit(-1)

	if not args.view:
		record_action(args)
	else:
		view_history()
	sys.exit(0)
from multiprocessing import cpu_count
import csv

# Whether to use CSV (recommended; easier to work with) or manual variables (legacy, not recommended except for testing)
use_csv_importer = True

# CSV Importer settings:

# Room requests csv file path:
room_request_csv_path = "requests.csv"
# See requests_example.csv for how this csv file should be setup
# The number in the second column represent the "modifier" - higher modifier = higher chance of getting their picks
# Example: Leadership gets 10, Seniors get 5, everyone else gets 0
# If you don't want to use this feature, set them all to 0
# MAKE SURE NAMES IN THE FIRST COLUMN ARE IDENTICAL IN EVERY WAY TO THE NAMES PUT IN THE REQUEST SECTION, OTHERWISE THIS WON'T WORK!


# Ignore first row? If your csv has headers, say True
ignore_first_row = True

# Room antirequests csv file path:
room_antireqest_csv_path = "antirequests.csv"
# See antirequests_example.csv for how this csv file should be setup


# Manual variable import settings can be found at the bottom of this file


# Manual pair score setting
# Allows you to manually set the score between any 2 students
# Student names must be in python ascii order
# Should be a list of tuple pairs to weights (positive or negative)
room_pairs = {}

# CPU Cores used
# This program will use ALL of your CPU power on the machine if allowed.
# Default: cpu_count() + 1
# This will use all of your computer's cpu to minimize runtime, but your computer may lag until completion
# Consider using cpu_count() - 2 if you want to leave it running in the background
cpu_cores = cpu_count() + 1

# Number of iterations
# Basically, the program has an element of randomness when it comes to finding optimal rooms
# The more iterations, the more likely the program will find a more optimal iteration, but the longer it takes
# The time the program takes to complete is linearly related to the number of iterations, but the number of iterations
# on average to find a better room increases exponentially
number_of_iterations = 500

# Random seed start
# Used to feed into the random number generator
# If you'd like to see consistent results, set this to a specific POSITIVE number like 53
# If you'd like the computer to do the randomness for you, set this to -1
seeding_random_seed = -1

# Request "weights"
# For each "pair", this is how many points the first, second, third, etc request gets.
# A "no match" weight is -1000000, aka will never match
room_pair_weights = [300, 100, 16, 14, 12, 10, 8, 6, 4, 2]

# Number of students per room
students_per_room = 6

# "Bonus" weight to add if rooming request is mutual
mutual_request_bonus = 20

# Manual variable importer settings:

# Room requests should be in this format:
"""

manual_room_requests = {
    "Student name": [10, "Student request 1", "Student request 2", "Student request 3"],
    "Student 2 name": [5, "Student request 1"],
    "Student without requests": [0],
}

"""
# The number in the first part of non-avoid brackets represent the "modifier" - higher modifier = higher chance of getting their picks
# Example: Leadership gets 10, Seniors get 5, everyone else gets 0
# MAKE SURE NAMES IN THE FIRST COLUMN ARE IDENTICAL IN EVERY WAY TO THE NAMES PUT IN THE REQUEST SECTION!

manual_room_requests = {}

# Room "Anti-requests"
# Simple list of tuples
# NOTE: the values in the tuple must be sorted in the order of python string comparsion,
# which is similar but not exactly like alphabetical sorting (it's ASCII sorting)
# Names should be identical as in above section
'''manual_room_antirequests = [
    ("Student 1", "Student 2"),
    ("Student 1", "Student 3"),
    ("Student 3", "Student 4"),
]'''
manual_room_antirequests = []

# Configuration processing code
# DO NOT EDIT ANYTHING BELOW THIS LINE

room_requests = {}
room_antirequests = []

if use_csv_importer:
    try:
        with open(room_request_csv_path, newline='') as room_request_csv:
            room_request_array = list(csv.reader(room_request_csv))
            if ignore_first_row:
                del room_request_array[0]
            for row in room_request_array:
                try:
                    room_requests[row[0]] = [float(row[1])] + row[2:]
                except ValueError:
                    print(
                        "The CSV file " + room_request_csv_path + " is not formatted correctly. Make sure the second column is the request weights!")
    except:
        print("Error opening file " + room_request_csv_path)
        exit(1)

    try:
        with open(room_antireqest_csv_path, newline='') as room_antirequest_csv:
            room_antirequest_array = list(csv.reader(room_antirequest_csv))
            for row in room_antirequest_array:
                try:
                    student1 = row[0]
                    student2 = row[1]
                    if student1 < student2:
                        room_antirequests.append((student1, student2))
                    else:
                        room_antirequests.append((student1, student2))
                except:
                    print("Invalid antirequest pair found, skipping")
                    print(row)
    except:
        print("Error opening file " + room_antireqest_csv_path)
        exit(1)

else:
    room_requests = manual_room_requests

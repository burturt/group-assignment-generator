from multiprocessing import Pool
import random
from datetime import datetime
from math import ceil
import settings
from pathlib import Path
import shutil
import sys
import csv


def get_antirequests():
    room_antirequests_sorted = []
    for request in settings.room_antirequests:
        if request[0] < request[1]:
            room_antirequests_sorted.append((request[0], request[1]))
        else:
            room_antirequests_sorted.append((request[1], request[0]))

    return room_antirequests_sorted


def main():
    room_pairs = calculate_pairing_happiness()
    # Run algorithm 100 times, select best result
    highest_score = 0
    best_arrangement = []
    with Pool(settings.cpu_cores) as pool:
        results = []

        for i in range(settings.number_of_iterations):
            results.append(pool.apply_async(generate_new_rooms, args=[room_pairs,
                                                                      settings.seeding_random_seed + i if settings.seeding_random_seed != -1 else -1]))
        pool.close()
        pool.join()
    count = 0
    for result in results:
        final_result = result.get()
        if highest_score < final_result[0]:
            highest_score = final_result[0]
            best_arrangement = final_result[1]
    best_arrangement_sorted = []
    for room in best_arrangement:
        best_arrangement_sorted.append(sorted(room))
    fancy_print_rooms(best_arrangement_sorted)
    print(calculate_room_happiness(best_arrangement_sorted, room_pairs))
    individual_happiness = calculate_individual_happiness(best_arrangement_sorted)

    # Save input and output in new output directory
    output_dir = Path("room-runs")
    if not output_dir.exists():
        output_dir.mkdir()
    directory_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + " " + str(settings.number_of_iterations)
    run_output_dir = Path("room-runs/" + directory_name)
    run_output_dir.mkdir()

    settings_file = Path("settings.py")
    destination_settings = run_output_dir / "settings.py"
    shutil.copy(settings_file, destination_settings)
    if settings.use_csv_importer:
        input_requests = Path(settings.room_request_csv_path)
        destination_input_requests = run_output_dir / "requests.csv"
        input_antirequests = Path(settings.room_antireqest_csv_path)
        destination_input_antirequests = run_output_dir / "antirequests.csv"
        shutil.copy(input_requests, destination_input_requests)
        shutil.copy(input_antirequests, destination_input_antirequests)
    output_file = run_output_dir / ("results-" + str(highest_score) + ".csv")
    with open(output_file, "w+") as output_csv:
        writer = csv.writer(output_csv, delimiter=",")
        writer.writerows(best_arrangement_sorted)
    output_file_pref = run_output_dir / ("individual_scores.csv")
    with open(output_file_pref, "w+") as output_csv:
        writer = csv.writer(output_csv, delimiter=",")
        writer.writerows(individual_happiness)


def calculate_pairing_happiness():
    room_pairs = settings.room_pairs

    antirequests = get_antirequests()
    for student, requests in settings.room_requests.items():
        if not requests:
            continue
        priority_weight = requests[0]
        ranked_list = requests[1:]
        for i in range(len(ranked_list)):
            student1 = student
            student2 = ranked_list[i]
            if (student1 > student2):
                student1, student2 = student2, student1
            if (student1, student2) in room_pairs:
                room_pairs[(student1, student2)] += settings.room_pair_weights[
                                                        i] + priority_weight + settings.mutual_request_bonus
            else:
                room_pairs[(student1, student2)] = settings.room_pair_weights[i] + priority_weight
    print("Students found:")
    for student1 in get_students():
        print(student1)
        for student2 in get_students():
            if (student1, student2) in antirequests:
                room_pairs[(student1, student2)] = -100000000
    return room_pairs


def generate_new_rooms(room_pairs, custom_random_seed=-1):
    rooms = generate_random_rooms(custom_random_seed)
    rooms = swap_brute_force(rooms, room_pairs)
    score = calculate_room_happiness(rooms, room_pairs)
    arrangement = rooms
    return (score, arrangement)


def calculate_room_happiness(rooms, room_pairs):
    room_happiness = 0
    for room in rooms:
        for i in range(len(room)):
            j = i
            while (j < len(room)):
                student1 = room[i]
                student2 = room[j]
                # Avoid 2+ empty seats
                if student1.startswith("ZZEMPTY") and student2.startswith("ZZEMPTY"):
                    room_happiness -= 1000
                if (student1 > student2):
                    student1, student2 = student2, student1
                room_happiness += room_pairs.get((student1, student2), 0)
                j += 1

    return room_happiness


def generate_random_rooms(custom_seed=-1):
    random_rooms = []
    students = get_students()
    # Add dummy students as "empty"
    for i in range(settings.students_per_room - len(students) % settings.students_per_room):
        students.append("ZZEMPTY" + str(i))
    # Shuffle at start to spread out "empty" students
    if not custom_seed == -1:
        random.seed(custom_seed)
    random.shuffle(students)

    for i in range(ceil(len(students) / settings.students_per_room)):
        random_rooms.append(
            students[i * settings.students_per_room:i * settings.students_per_room + settings.students_per_room])

    return random_rooms


def get_students():
    return list(settings.room_requests.keys())


def swap_brute_force(rooms, room_pairs):
    counter = 0
    changes = True
    while changes:
        changes = False
        for i1 in range(len(rooms)):
            for i2 in range(settings.students_per_room):
                for j1 in range(len(rooms)):
                    for j2 in range(settings.students_per_room):
                        orig_happiness = calculate_room_happiness(rooms, room_pairs)
                        rooms[i1][i2], rooms[j1][j2] = rooms[j1][j2], rooms[i1][i2]
                        new_happiness = calculate_room_happiness(rooms, room_pairs)
                        counter += 1
                        if (orig_happiness >= new_happiness):
                            rooms[i1][i2], rooms[j1][j2] = rooms[j1][j2], rooms[i1][
                                i2]
                        else:
                            changes = True
    print("Iteration happiness: " + str(calculate_room_happiness(rooms, room_pairs)))
    return rooms


def fancy_print_rooms(rooms):
    for room in rooms:
        print(room)

def calculate_individual_happiness(rooms):
    output_array = []
    room_requests = settings.room_requests
    for room in rooms:
        for student in room:
            if student.startswith("ZZEMPTY"):
                continue
            student_choices = room_requests[student]
            student_choices.pop(0)
            happiness = 0
            i = 0
            while i < len(student_choices):
                if student_choices[i] == "":
                    student_choices.pop(i)
                    continue
                if student_choices[i] in room:
                    happiness += settings.room_pair_weights[i]
                i += 1
            output_array.append([student, happiness, str(sum(settings.room_pair_weights[0:len(student_choices)]))])
            print(student + ": " + str(happiness) + "/" + str(sum(settings.room_pair_weights[0:len(student_choices)])))

    return output_array

if __name__ == "__main__":
    # Verify proper python version
    if not sys.version_info.major == 3 and sys.version_info.minor == 8:
        print("This script is tested on python 3.8 ONLY. You are currently running " + sys.version())
    # Calculate runtime
    start = datetime.now()
    print("Started at: " + str(start))
    main()
    print("Ended at: " + str(datetime.now()))
    print("Time to completion: " + str(datetime.now() - start))





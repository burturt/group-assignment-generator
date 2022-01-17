from multiprocessing import Pool, cpu_count
import random
from datetime import datetime
from math import ceil
import settings

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
    with Pool(10) as pool:
        results = []

        for i in range(settings.number_of_iterations):
            results.append(pool.apply_async(generate_new_rooms, args=[room_pairs, settings.seeding_random_seed + i if settings.seeding_random_seed != -1 else -1]))
            #current_score = rooms[0]
            #if (highest_score < current_score):
            #    best_arrangement = rooms[1]
            #    highest_score = current_score
        pool.close()
        pool.join()
    count = 0
    for result in results:
        final_result = result.get()
        if highest_score < final_result[0]:
            highest_score = final_result[0]
            best_arrangement = final_result[1]
    fancy_print_rooms(best_arrangement)
    print(calculate_room_happiness(best_arrangement, room_pairs))

def calculate_pairing_happiness():
    room_pairs = {}
    antirequests = get_antirequests()
    for student, requests in settings.room_requests.items():
        if not requests:
            continue;
        priority_weight = requests[0]
        ranked_list = requests[1:]
        for i in range(len(ranked_list)):
            student1 = student
            student2 = ranked_list[i]
            if (student1 > student2):
                student1, student2 = student2, student1
            if (student1, student2) in room_pairs:
                room_pairs[(student1, student2)] += settings.room_pair_weights[i] + priority_weight + settings.mutual_request_bonus
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
        random_rooms.append(students[i * settings.students_per_room:i * settings.students_per_room + settings.students_per_room])

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
        print(sorted(room))

if __name__ == "__main__":
    # Calculate runtime
    start = datetime.now()
    print("Started at: " + str(start))
    main()
    print("Ended at: " + str(datetime.now()))
    print("Time to completion: " + str(datetime.now()-start))


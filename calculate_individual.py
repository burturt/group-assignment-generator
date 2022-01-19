# Take in csv file called "rooms.csv" and calculate individual happiness
import csv
import main

try:
    with open('rooms.csv', newline='') as rooms_csv:
        rooms_array = list(csv.reader(rooms_csv))
    students = []
    for room in rooms_array:
        for student in room:
            students.append(student)
            print(student)

except:
    print("Error opening file")
    exit(1)


print(main.calculate_room_happiness(rooms_array, main.calculate_pairing_happiness()))
individual_happiness = main.calculate_individual_happiness(rooms_array)

for student in individual_happiness:
    print(student[0] + ": " + str(student[1]) + "/" + str(student[2]))
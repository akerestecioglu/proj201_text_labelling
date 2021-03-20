import pandas as pd
import numpy as np
import math

def get_usernames():
    df = pd.read_csv('students_info.csv')
    usernames = []
    # add username of the student to the list of usernames
    for index, row in df.iterrows():
        # get username from email adress
        username = row['Email address'][:row['Email address'].index('@')]
        usernames.append(username)
    return usernames

def find_all_scores(student, file_name):
    scores = []
    with open(file_name, 'r') as file:
        for line in file.readlines():
            if  line.find(student) != -1:
                # , ile split yapınca -->>  0.8595183486238532)
                dirty_str = line.split(',')[-1]
                score = float(dirty_str.strip()[:-1])
                scores.append(score)
    return scores

def print_average_scores(students, input_file_name, output_file_name):
    with open(output_file_name, 'w') as output_file:
        for student in students:
            scores = find_all_scores(student, input_file_name)
            if len(scores) > 0:
                not_nan_scores = []
                for i in scores:
                    if not math.isnan(i):
                        not_nan_scores.append(i)
                average = sum(not_nan_scores)/len(scores)
                output_file.write(student + ' - ' + str(average) + ' - ' + str(len(scores)) + '\n')
            else:
                output_file.write(student + ' - NO ANNOTATION\n')


def convert_to_csv(input_file_name, output_file_name):
    with open(input_file_name, 'r') as in_file:
        with open(output_file_name, 'w') as out_file:
            for line in in_file.readlines():
                items = line.split('-')
                if len(items) == 3:
                    new_line = items[0].strip() + ',' + items[1].strip() + ',' + items[2].strip() + '\n'
                    out_file.write(new_line)
                else:
                    new_line = items[0].strip() + ',' + items[1].strip() + ',' + items[1].strip() + '\n'
                    out_file.write(new_line)


if __name__ == '__main__':
    #students = get_usernames()
    #print_average_scores(students, 'eq-db-01-out.txt', 'eq-db-01-average.txt')
    convert_to_csv('ner-db-03-average.txt', 'ner-db-03-average.csv')
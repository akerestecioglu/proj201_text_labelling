import pandas as pd
import os
import portpicker
import time
from add_users_to_db import add_users_to_db, output_credentials, get_usernames
from distribute_sentences import distribute_sentences
from connect_db import find_average_kappa_per_student, find_not_annotated_example_counts
from project import db
from project.models import User


# function to get the set of all ids of processes in a file
def get_all_processes(file_name):
    with open(file_name) as file:
        lines = file.readlines()
    processes = set()
    for line in lines[1:]:
        elements = line.split()
        if elements[3] == 'python' or elements[3] == 'prodigy':
            processes.add(elements[0])
    return processes


# function to write process ids that belong to a user to a file
def write_processes_to_file(processes, process_out_file_name, kill_ids_out_file_name):
    # username and pids of a user in each line
    with open(process_out_file_name, 'w') as file:
        for username, pids in processes.items():
            new_line = username + ','
            for process in pids:
                new_line += str(process) + ','
            new_line = new_line[:-1] + '\n'
            file.write(new_line)
    # one kill id in each line
    with open(kill_ids_out_file_name, 'w') as file:
        for pids in processes.values():
            for process in pids:
                file.write(str(process) + '\n')


# function to start all prodigy processes of students, store the corresponding process ids in a file
def start_prodigy(usernames, task_type, db_name, labels, user_process_file_name, kill_ids_file_name):
    os.environ['PRODIGY_HOST'] = "0.0.0.0"
    # a dictionary to store the prodigy related process ids created for each user
    new_pids = {}
    for username in usernames:
        # pick an available port
        available_port = int(portpicker.pick_unused_port())
        os.environ['PRODIGY_PORT'] = str(available_port)
        # store the process ids before starting prodigy
        os.system('ps -u akerestecioglu >> before_{}.txt'.format(username))
        before_set = get_all_processes('before_{}.txt'.format(username))
        # start prodigy with the right task type (ner or text_classification)
        if task_type == 'ner':
            os.system('prodigy ner.manual {}-{} blank:en ./{}-{}.jsonl --label {} &'.format(username, db_name, username, db_name, labels))
        elif task_type == 'text_classification':
            os.system('prodigy textcat.manual {}-{} ./{}-{}.jsonl --label {} &'.format(username, db_name, username, db_name, labels))
        # sleep for 5 seconds
        time.sleep(5)
        # store the process ids before starting prodigy
        os.system('ps -u akerestecioglu >> after_{}.txt'.format(username))
        after_set = get_all_processes('after_{}.txt'.format(username))
        # find the process ids that showed up after starting prodigy
        new_processes = after_set - before_set
        # add the new key,value pair to the dictionary of process ids
        new_pids[username] = new_processes

        current_user = User.query.filter_by(username=username).first()
        # save the port information to db
        current_user.update_last_process(available_port)
        db.session.commit()
        # delete files with process ids
        os.remove('before_{}.txt'.format(username))
        os.remove('after_{}.txt'.format(username))
    # write all usernames and corresponding process ids to a file
    write_processes_to_file(new_pids, user_process_file_name, kill_ids_file_name)


if __name__ == '__main__':
    # PARAMETER VALUES
    # students_info_file_path should be csv, header should be Surname,First name,ID number,Email address
    students_info_file_path = 'example_students.csv'
    # path of the output file that the student credentials will be written into
    student_credentials_out_file_path = 'credentials.txt'
    # the path of the file which contains all examples to be distributed
    examples_file_path = 'deprem.jsonl'
    # postfix of the db name that prodigy will store the annotations in
    # the db names will be in the following format: $username-$db_name
    db_name_postfix = 'ner-db-01'
    # the directory where the files with distributed examples will be created in
    examples_output_directory = os.getcwd()
    # number of examples to be annotated by each student
    num_examples_per_student = 60
    # number of students to annotate each example
    num_students_per_example = 2
    # label options in prodigy, should be a string which labels are separated with commas
    task_type = 'ner'
    labels = 'ADANA,BURSA,CEYHAN,DENIZLI'
    # path of the output file that ids of prodigy processes that are created for each user is written into
    process_ids_out_file_path = 'process_ids.txt'
    # path of the output file in which there is a kill id of a prodigy process in each line
    kill_ids_out_file_path = 'kill_ids.txt'
    # path of the output file which average cohen's kappa scores will be written into
    avg_kappa_out_file_path = f'{db_name_postfix}-average.csv'
    # path of the output file which number of not annotated examples will be written into
    no_annotation_counts_out_file_path = f'no-annotation-counts-{db_name_postfix}.txt'

    # FUNCTION CALLS
    add_users_to_db(students_info_file_path)
    output_credentials(students_info_file_path, student_credentials_out_file_path)
    usernames = get_usernames(students_info_file_path)
    distribute_sentences(examples_file_path, examples_output_directory, db_name_postfix, usernames, num_examples_per_student, num_students_per_example)
    time.sleep(5)
    start_prodigy(usernames, task_type, db_name_postfix, labels, process_ids_out_file_path, kill_ids_out_file_path)
    #find_average_kappa_per_student(db_name_postfix, task_type, usernames, avg_kappa_out_file_path)
    #find_not_annotated_example_counts(db_name_postfix, task_type, no_annotation_counts_out_file_path)

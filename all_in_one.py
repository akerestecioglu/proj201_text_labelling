import pandas as pd
from add_users_to_db import add_users_to_db, output_credentials
from distribute_sentences import distribute_sentences
from connect_db import find_average_kappa_per_student, find_not_annotated_example_counts
import os
import portpicker
from project import db
from project.models import User
import time
# import prodigy

# function to get the list of all usernames in a file
def get_usernames(file_name):
    df = pd.read_csv(file_name)
    usernames = []
    # add username of the student to the list of usernames
    for index, row in df.iterrows():
        # get username from email adress
        username = row['Email address'][:row['Email address'].index('@')]
        usernames.append(username)
    return usernames


# function to get the set of all pids of processes in a file
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
def write_processes_to_file(processes, out_file_name):
    with open(out_file_name, 'w') as file:
        for username, pids in processes.items():
            new_line = username + ','
            for process in pids:
                new_line += str(process) + ','
            new_line = new_line[:-1] + '\n'
            file.write(new_line)


# function to start all prodigy processes of students, store the corresponding process ids in a file
def start_prodigy(usernames, task_type, db_name, labels, process_file_name):
    os.environ['PRODIGY_HOST'] = "0.0.0.0"
    new_pids = {}
    for username in usernames:
        # port 0 olursa otomatik olarak bos porta atabilir
        available_port = int(portpicker.pick_unused_port())
        os.environ['PRODIGY_PORT'] = str(available_port)
        os.system('ps -u akerestecioglu >> before_{}.txt'.format(username))
        before_set = get_all_processes('before_{}.txt'.format(username))
        if task_type == 'ner':
            # db isimleri $username-ner-db-01 okunacak dosya da $username-ner-01.jsonl
            os.system('prodigy ner.manual {}-{} blank:en ./{}-{}.jsonl --label {} &'.format(username, db_name, username, db_name, labels))
            '''
            prodigy.serve(
                'ner.manual {}-{} blank:en ./{}-{}.jsonl --label {}'.format(username, db_name, username, db_name, labels),
                port=available_port)
            '''
            # os.system('prodigy ner.manual eagaev-ner-db-01 blank:en ./eagaev-ner-01.jsonl --label PERSON,ORG,PRODUCT,LOCATION &')
        elif task_type == 'text_classification':
            os.system('prodigy textcat.manual {}-{} ./{}-{}.jsonl --label {} &'.format(username, db_name, username, db_name, labels))
            '''
            prodigy.serve(
                'textcat.manual {}-{} ./{}-{}.jsonl --label {}'.format(username, db_name, username, db_name, labels),
                port=available_port)
            '''
        time.sleep(5)
        os.system('ps -u akerestecioglu >> after_{}.txt'.format(username))
        after_set = get_all_processes('after_{}.txt'.format(username))
        new_processes = after_set - before_set
        new_pids[username] = new_processes
        # prodigy.serve("ner.manual ner_news_headlines blank:en ./news_headlines.jsonl --label PERSON,ORG,PRODUCT,LOCATION", port=available_port)

        current_user = User.query.filter_by(username=username).first()
        # save the port, process_id
        current_user.update_last_process(available_port)
        db.session.commit()
        os.remove('before_{}.txt'.format(username))
        os.remove('after_{}.txt'.format(username))
    write_processes_to_file(new_pids, process_file_name)


if __name__ == '__main__':
    # students_info_file_path should be csv, header should be Surname,First name,ID number,Email address
    students_info_file_path = 'example_students.csv'
    # path of the output file that the student credentials will be written into
    student_credentials_out_file_path = 'credentials.txt'
    # postfix of the db name that prodigy will store the annotations in
    # the db names will be in the following format: $username-$db_name
    db_name_postfix = 'ner-db-01'
    # the directory where the files with distributed examples will be created in
    examples_output_directory = '/Users/akerestecioglu/Desktop/PROJ201-ReyyanYeniterzi'
    # number of examples to be annotated by each student
    num_examples_per_student = 60
    # number of students to annotate each example
    num_students_per_example = 2
    # label options in prodigy, should be a string which labels are separated with commas
    labels = 'ADANA,BURSA,CEYHAN,DENIZLI'
    # path of the output file that ids of prodigy processes that are created for each user is written intp
    process_ids_out_file_path = 'process_ids.txt'
    add_users_to_db(students_info_file_path)
    output_credentials(students_info_file_path, student_credentials_out_file_path)
    usernames = get_usernames(students_info_file_path)
    distribute_sentences('deprem.jsonl', examples_output_directory, db_name_postfix, usernames, num_examples_per_student, num_students_per_example)
    time.sleep(5)
    start_prodigy(usernames, 'ner', db_name_postfix, labels, process_ids_out_file_path)
    #find_average_kappa_per_student(db_name, 'ner', usernames, f'{db_name}-average.csv')
    #find_not_annotated_example_counts(db_name, 'ner', f'no-annotation-counts-{db_name}.txt')

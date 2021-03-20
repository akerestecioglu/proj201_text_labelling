import pandas as pd
import random
from collections import defaultdict

# returns the list of usernames of students
def get_usernames():
    df = pd.read_csv('students_info.csv')
    usernames = []
    # add username of the student to the list of usernames
    for index, row in df.iterrows():
        # get username from email adress
        username = row['Email address'][:row['Email address'].index('@')]
        usernames.append(username)
    return usernames


# reads the file and returns the list of lines
def read_data(file_name):
    data = []
    with open(file_name) as file:
        for line in file.readlines():
            data.append(line)
    return data


# selects a random subset of length example_num within data
def select_sentences(data, example_num):
    nums = random.sample(range(len(data)), example_num)
    nums.sort()
    selected_sents = [data[i] for i in nums]
    return selected_sents


# assigns 60 sentences to each student, every sentence assigned to exactly 2 students
def assign_sents_to_students(sentences, usernames, sents_per_student, students_per_sent):
    studs_and_sents = defaultdict(list)
    '''
    for i in range(60):
        unassigned_studs = usernames.copy()
        print(len(unassigned_studs))
        for j in range(17):
            studs = random.sample(unassigned_studs, 2)
            for stud in studs:
                studs_and_sents[stud].append(sentences[17*i+j])
                unassigned_studs.remove(stud)
    '''
    cnt = 0
    for sentence in sentences:
        for j in range(students_per_sent):
            studs_and_sents[usernames[cnt]].append(sentence)
            cnt = (cnt + 1) % len(usernames)
    return studs_and_sents


# write the examples assigned to students to jsonl files
def sentences_to_file(my_dict, db_name, output_directory):
    for username, sents in my_dict.items():
        with open(f'{output_directory}/{username}-{db_name}.jsonl', 'w') as out_file:
            content = ''
            for sent in sents:
                content += str(sent).strip() + '\n'
            out_file.write(content)


def distribute_sentences(file_name, output_directory, db_name, usernames, sents_per_student, students_per_sent):
    data = read_data(file_name)
    num_examples = int(len(usernames) * sents_per_student / students_per_sent)
    sentences = select_sentences(data, num_examples)
    sents_students = assign_sents_to_students(sentences, usernames, sents_per_student, students_per_sent)
    sentences_to_file(sents_students, db_name, output_directory)



''' 
    def distribute_sentences_with_all_sents(file_name, usernames):
    sentences = read_data(file_name)
    sents_students = assign_sents_to_students(sentences, usernames)
    sentences_to_file(sents_students)
'''


if __name__ == '__main__':
    # PARAMETER VALUES
    examples_file_path = 'deprem.jsonl'
    # number of examples to be annotated by each student
    num_examples_per_student = 60
    # number of students to annotate each example
    num_students_per_example = 2

    # FUNCTION CALLS
    usernames = get_usernames()
    data = read_data(examples_file_path)
    sentences = select_sentences(data, int(len(usernames) * num_examples_per_student / num_students_per_example))
    sents_students = assign_sents_to_students(sentences, usernames, num_examples_per_student, num_students_per_example)
    sentences_to_file(sents_students)
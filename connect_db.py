from prodigy.components.db import connect
from collections import defaultdict
from sklearn.metrics import cohen_kappa_score
import math
from add_users_to_db import get_usernames


# returns the list of names of datasets in prodigy that end with db_name
def get_datasets(db_name):
    db = connect()
    all_dataset_names = db.datasets
    relevant_datasets = []
    for dataset in all_dataset_names:
        if dataset.endswith(db_name):
            relevant_datasets.append(dataset)
    return relevant_datasets


# groups documents by text id
# returns a dict where keys are text ids and values are lists of annotations
def group_by_id(datasets):
    docs = defaultdict(list)
    for dataset in datasets:
        # connect to prodigy db
        db = connect()
        # get the dataset as a list of annotated examples
        examples = db.get_dataset(dataset)
        for example in examples:
            # append example to the list of examples with the same id if the annotation is accepted
            if example['answer'] == 'accept':
                # "id" can be lowercase or uppercase, it doesn't matter
                try:
                    docs[example['meta']['id']].append((example, dataset[:dataset.find('-')]))
                except:
                    docs[example['meta']['ID']].append((example, dataset[:dataset.find('-')]))
    return docs


# returns a dict where keys are token indices in a sentence and values are labels assigned to them
def find_tagged_tokens(annotation):
    my_dict = {}
    for span in annotation['spans']:
        for token_idx in range(span['token_start'], span['token_end'] + 1):
            my_dict[token_idx] = span['label']
    return my_dict


# function to create 2 lists that store labels assigned by students
def get_labels(annotation1, annotation2, db_type):
    arr1 = []
    arr2 = []
    if db_type == 'ner':
        tagged_tokens1 = find_tagged_tokens(annotation1)
        for i in range(len(annotation1['tokens'])):
            if i in tagged_tokens1:
                arr1.append(tagged_tokens1[i])
            else:
                arr1.append('OTHER')
        tagged_tokens2 = find_tagged_tokens(annotation2)
        for i in range(len(annotation2['tokens'])):
            if i in tagged_tokens2:
                arr2.append(tagged_tokens2[i])
            else:
                arr2.append('OTHER')
    else:
        options = [x['id'] for x in annotation1['options']]
        for option in options:
            if option in annotation1['accept']:
                arr1.append('1')
            else:
                arr1.append('0')
            if option in annotation2['accept']:
                arr2.append('1')
            else:
                arr2.append('0')
    return arr1, arr2


# function to find the cohen's kappa score of all pairs that annotate the same text
# returns a dict where keys are tuples (text_id, student1, student2), and values are scores(float)
def find_cohen_kappa(docs, db_type):
    scores = {}
    for text_id, annotations in docs.items():
        for i in range(len(annotations)):
            if db_type == 'ner':
                if 'spans' in annotations[i][0].keys():
                    for j in range(i+1, len(annotations)):
                        if 'spans' in annotations[j][0].keys():
                            # arr1 and arr2 are lists of labels
                            arr1, arr2 = get_labels(annotations[i][0], annotations[j][0], db_type)
                            scores[(text_id, annotations[i][1], annotations[j][1])] = cohen_kappa_score(arr1, arr2)
            else:
                for j in range(i + 1, len(annotations)):
                    if 'accept' in annotations[j][0].keys():
                        # arr1 and arr2 are lists of labels
                        arr1, arr2 = get_labels(annotations[i][0], annotations[j][0], db_type)
                        scores[(text_id, annotations[i][1], annotations[j][1])] = cohen_kappa_score(arr1, arr2)
    return scores


# returns a dict of pairwise kappa scores
def pairwise_cohens_kappa_scores(datasets, db_type):
    docs = group_by_id(datasets)
    scores = find_cohen_kappa(docs, db_type)
    return scores


# returns the average kappa score of the student and the number of annotated examples
def average_cohens_kappa_score(student, pairwise_scores):
    student_scores = []
    for k,v in pairwise_scores.items():
        if student in k:
            student_scores.append(v)
    # if there is any annotation
    if len(student_scores) > 0:
        not_nan_scores = []
        for i in student_scores:
            if not math.isnan(i):
                not_nan_scores.append(i)
        average = sum(not_nan_scores) / len(student_scores)
    # return 0 if there is no annotation
    else:
        average = 0
    return average, len(student_scores)


# function to write the average kappa scores and number of annotated examples to a file
def print_average_scores(students, output_file_name, pairwise_scores):
    with open(output_file_name, 'w') as output_file:
        output_file.write('username,average_kappa,number_of_annotations\n')
        for student in students:
            average, annotation_count = average_cohens_kappa_score(student, pairwise_scores)
            output_file.write(student + ',' + str(average) + ',' + str(annotation_count) + '\n')


# function to calculate and print average kappa score for each student
def find_average_kappa_per_student(dataset, db_type, usernames, output_file_name):
    # list of dataset names that end with the argument
    datasets = get_datasets(dataset)
    pairwise_scores = pairwise_cohens_kappa_scores(datasets, db_type)
    print_average_scores(usernames, output_file_name, pairwise_scores)


# function to write the number of not annotated examples of each student to a file
def find_not_annotated_example_counts(dataset, db_type, output_file_name):
    datasets = get_datasets(dataset)
    docs = group_by_id(datasets)
    counts = defaultdict(int)
    for text_id, anns in docs.items():
        for ann in anns:
            if db_type == 'ner':
                if 'spans' not in ann[0].keys():
                    username = ann[1]
                    counts[username] += 1
            else:
                if len(ann[0]['accept']) == 0:
                    username = ann[1]
                    counts[username] += 1
    # write counts to file
    with open(output_file_name, 'w') as file:
        for username, count in counts.items():
            file.write(username + ': ' + str(count) + '\n')


if __name__ == '__main__':
    # PARAMETERS
    db_name_postfix = 'ner-db-01'
    task_type = 'ner'
    students_info_file_path = 'example_students.csv'
    avg_kappa_out_file_path = f'{db_name_postfix}-average.csv'
    no_annotation_counts_out_file_path = f'no-annotation-counts-{db_name_postfix}.txt'

    # FUNCTION CALLS
    usernames = get_usernames(students_info_file_path)
    find_average_kappa_per_student(db_name_postfix, task_type, usernames, avg_kappa_out_file_path)
    find_not_annotated_example_counts(db_name_postfix, task_type, no_annotation_counts_out_file_path)

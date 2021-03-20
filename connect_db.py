from prodigy.components.db import connect
from collections import defaultdict
from sklearn.metrics import cohen_kappa_score
import math

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
        db = connect()
        examples = db.get_dataset(dataset)
        for example in examples:
            # append data to the list of data with the same id if the answer is accept
            if example['answer'] == 'accept':
                try:
                    docs[example['meta']['id']].append((example, dataset[:dataset.find('-')]))
                except:
                    docs[example['meta']['ID']].append((example, dataset[:dataset.find('-')]))
    return docs


# returns a dict where keys are token indices and values are labels given to them
def find_tagged_tokens(annotation):
    my_dict = {}
    for span in annotation['spans']:
        for token_idx in range(span['token_start'], span['token_end'] + 1):
            my_dict[token_idx] = span['label']
    return my_dict

'''
# function to create 2 lists that store labels assigned by students
def group_by_token(annotation1, annotation2):
    arr1 = []
    tagged_tokens1 = find_tagged_tokens(annotation1)
    for i in range(len(annotation1['tokens'])):
        if i in tagged_tokens1:
            arr1.append(tagged_tokens1[i])
        else:
            arr1.append('OTHER')
    arr2 = []
    tagged_tokens2 = find_tagged_tokens(annotation2)
    for i in range(len(annotation2['tokens'])):
        if i in tagged_tokens2:
            arr2.append(tagged_tokens2[i])
        else:
            arr2.append('OTHER')
    return arr1, arr2
'''

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

'''
# function to create 2 lists that store labels assigned by students
def group_by_token(annotation1, annotation2):
    arr1 = []
    arr2 = []
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
'''

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


# function to print all tokens and the labels assigned by students
def print_annotations(doc_id, files):
    docs = group_by_id(files)
    # keys are usernames, values are dicts (returned by find_tagged_tokens())
    tags = {}
    for elm in docs[doc_id]:
        username = elm[1]
        annotation = elm[0]
        tagged_tokens = find_tagged_tokens(annotation)
        tags[username] = tagged_tokens
    tokens = docs[doc_id][0][0]['tokens']
    print(doc_id)
    cnt = 0
    for token in tokens:
        labels = ''
        for name, annts in tags.items():
            # if the token is labeled by the student
            if cnt in annts:
                labels += f' {name}:{annts[cnt]}'
            # print no_label if it is not labeled by the student
            else:
                labels += f' {name}:no_label'
        print(token['text'] + labels)
        cnt += 1

# returns a dict of pairwise kappa scores
def pairwise_cohens_kappa_scores(datasets, db_type):
    docs = group_by_id(datasets)
    scores = find_cohen_kappa(docs, db_type)
    return scores


# returns the average score of the student and the number of annotated examples
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


def print_average_scores(students, output_file_name, pairwise_scores):
    with open(output_file_name, 'w') as output_file:
        output_file.write('username,average_kappa,number_of_annotations\n')
        for student in students:
            average, annotation_count = average_cohens_kappa_score(student, pairwise_scores)
            output_file.write(student + ',' + str(average) + ',' + str(annotation_count) + '\n')


def find_average_kappa_per_student(dataset, db_type, students, output_file_name):
    # list of dataset names that end with the argument
    datasets = get_datasets(dataset)
    pairwise_scores = pairwise_cohens_kappa_scores(datasets, db_type)
    print_average_scores(students, output_file_name, pairwise_scores)


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
    with open(output_file_name, 'w') as file:
        for username, count in counts.items():
            file.write(username + ': ' + str(count) + '\n')



if __name__ == '__main__':
    # list of dataset names that end with the argument
    datasets = get_datasets('ner-db-01')
    # output pairwise cohens kappa scores
    scores = pairwise_cohens_kappa_scores(datasets, 'ner')
    # output annotation coverage

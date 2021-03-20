import json
from collections import defaultdict
from sklearn.metrics import cohen_kappa_score


# groups documents by text id
# returns a dict where keys are text ids and vals are lists of annotations
def group_by_id(files):
    docs = defaultdict(list)
    for file_name in files:
        with open(file_name) as file:
            for line in file.readlines():
                data = json.loads(line)
                # append data to the list of data with the same id if the answer is accept
                if data['answer'] == 'accept':
                    docs[data['meta']['id']].append((data, file_name[:file_name.find('-')]))
    return docs


# returns a dict where keys are token indices and values are labels given to them
def find_tagged_tokens(annotation):
    my_dict = {}
    for span in annotation['spans']:
        for token_idx in range(span['token_start'], span['token_end'] + 1):
            my_dict[token_idx] = span['label']
    return my_dict


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


# function to find the cohen's kappa score of all pairs that annotate the same text
# returns a dict where keys are tuples (text_id, student1, student2), and values are scores(float)
def find_cohen_kappa(docs):
    scores = {}
    for text_id, annotations in docs.items():
        for i in range(len(annotations)):
            for j in range(i+1, len(annotations)):
                # arr1 and arr2 are lists of labels
                arr1, arr2 = group_by_token(annotations[i][0], annotations[j][0])
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


if __name__ == '__main__':
    files = ['alpercakar-ner-db-01.json', 'alperenyildiz-ner-db-01.json', 'burakbatman-ner-db-01.json',
             'caltinuzengi-ner-db-01.json', 'colakulas-ner-db-01.json', 'dogru-ner-db-01.json']
    docs = group_by_id(files)
    scores = find_cohen_kappa(docs)
    print("Cohen's Kappa Scores:\n******************")
    print(scores)
    #print('All Tokens and Labels:\n******************')
    #print_annotations('Hurriyet621', files)

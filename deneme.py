
import pickle
from sklearn.metrics import cohen_kappa_score
from collections import defaultdict


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



# function to find the cohen's kappa score of all pairs that annotate the same text
# returns a dict where keys are tuples (text_id, student1, student2), and values are scores(float)
def find_cohen_kappa(docs):
    scores = {}
    for text_id, annotations in docs.items():
        for i in range(len(annotations)):
            if 'accept' in annotations[i][0].keys():
                try:
                    for j in range(i+1, len(annotations)):
                        if 'accept' in annotations[j][0].keys():
                            # arr1 and arr2 are lists of labels
                            arr1, arr2 = group_by_token(annotations[i][0], annotations[j][0])
                            scores[(text_id, annotations[i][1], annotations[j][1])] = cohen_kappa_score(arr1, arr2)
                except:
                    pass
    return scores



def find_not_annotated_docs(docs):
    for text_id, anns in docs.items():
        for ann in anns:
            if len(ann[0]['accept']) == 0:
                print(text_id, ann[1])

def pairwise_cohens_cappa_scores(docs):
    scores = find_cohen_kappa(docs)
    print("Cohen's Kappa Scores:\n******************")
    for item in scores.items():
        print(item)

def parse_no_spans(no_span_file):
    counts = defaultdict(int)
    with open(no_span_file, 'r') as file:
        for line in file.readlines():
            items = line.strip().split()
            username = items[1]
            counts[username] += 1
    with open('no-annotation-counts-ner-db-01.txt', 'w') as file:
        for username, count in counts.items():
            file.write(username + ': ' + str(count) + '\n')



if __name__ == '__main__':
    docs = pickle.load(open('eq_docs01.p', 'rb'))
    # output pairwise cohens kappa scores

    pairwise_cohens_cappa_scores(docs)
    # output annotation coverage

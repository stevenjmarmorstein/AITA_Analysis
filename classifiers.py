import json
import random

import nltk
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import classification_report


def main(*args):
    pos_labels = ["NTA", "YTA", "NAH", "ESH", "INFO"]

    raw_data = get_data()
    cleaned_inputs = clean_posts(raw_data['title'], raw_data['body'])
    labels = raw_data['label']
    # should remove INFO posts here
    data_pairs = [(cleaned_inputs[i], labels[i]) for i in range(len(labels))]
    # Dividing the data 65/35 into train and test
    random.shuffle(data_pairs)
    x_train = [data_pairs[i][0] for i in range(round(len(labels)*.65))]
    y_train = [data_pairs[i][1] for i in range(round(len(labels)*.65))]
    x_test = [data_pairs[i][0] for i in range((round(len(labels)*.65)), len(labels))]
    y_test = [data_pairs[i][1] for i in range((round(len(labels)*.65)), len(labels))]



    nb = Pipeline([('vect', CountVectorizer()),
               ('tfidf', TfidfTransformer()),
               ('clf', MultinomialNB()),
              ])

    nb.fit(x_train, y_train)

    y_predicted = nb.predict(x_test)
    print(y_predicted)
    print('accuracy %s' % accuracy_score(y_predicted, y_test))
    print(classification_report(y_test, y_predicted))


def clean_posts(titles, bodies):
    """
    Takes a pair of lists of strings and cleans them, removing stopwords and
    normalizing capitalization before returning a list of lists of words, where
    the words from each element of the pair have been combined into one list.
    """
    # TODO: replace punctuation with spaces
    # remove [removed] posts
    stopwords_set = set(nltk.corpus.stopwords.words('english'))
    posts = []
    for i in range(len(titles)):
        point = (titles[i] + " " + bodies[i]).lower()
        point_words = nltk.word_tokenize(point)
        # removing stop words:
        point_words = " ".join([word for word in point_words if word not in stopwords_set])
        posts.append(point_words)

    return posts



def get_data():
    """
    Reads the data from data.json and returns the dict that should be stored
    there. Data should be a dictionary with three string keys: label, title,
    and body. The data should be ordered so that the ith post in the collection
    corresponds to the ith title, body, and label.
    """
    filename = "big_data.json"
    f = open(filename, "r")
    json_string = f.read()
    dict = json.loads(json_string)
    return dict


if __name__ == "__main__":
    main()

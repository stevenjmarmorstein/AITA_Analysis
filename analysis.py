#!/usr/bin/env python

# Author: Steven Marmorstein
from nltk import *
import json
import random


class Analysis(object):

    def __init__(self, *args):
        posts_dict = self.get_data()
        labels = posts_dict["label"]
        titles = posts_dict["title"]
        bodies = posts_dict["body"]

        all_words = []
        for title in titles:
            title_words = [w.lower() for w in word_tokenize(title)]
            all_words.extend(title_words)
        for body in bodies:
            body_words = [w.lower() for w in word_tokenize(body)]
            all_words.extend(body_words)
        all_words_freqdist = FreqDist(w for w in all_words)
        self.word_features = all_words_freqdist.most_common(1000)
        print(self.word_features, "\n\n\n\n\n\n")
        print(all_words_freqdist)

        data_triples = []
        # This dictionary will score the counts of each label:
        counts = { "NAH":0, "ESH":0, "NTA":0, "YTA":0, "INFO":0 }
        print(len(labels))

        # Loop counts the number of posts with each label and makes a tuple of
        # the text and its label:
        data_triples = []
        for i in range(len(labels)):
            counts[labels[i]] += 1
            if(labels[i] != "INFO"):
                data_triples.append((titles[i], bodies[i], labels[i]))
        print(counts)
        random.shuffle(data_triples)
        N = len(data_triples)
        feature_label_pairs = []
        for trip in data_triples:
            feature_label_pairs.append((self.extract_features(trip), trip[2]))

        train_set = feature_label_pairs[:N//2]
        dev_set = feature_label_pairs[N//2:]
        classifier = NaiveBayesClassifier.train(train_set)
        print(classify.accuracy(classifier, dev_set))
        classifier.show_most_informative_features(20)


    def extract_features(self, trip):
        """
        Returns a dictionary with string keys and boolean values that indicate
        whether or not a word is found in the title+body of a post.
        """

        title = trip[0]
        body = trip[1]
        text = title + " " + body
        text_words = set(word_tokenize(text))
        features = {}
        for word in self.word_features:
            features['contains({})'.format(word[0])] = (word[0] in text_words)
        return features


    def get_data(self):
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
    Classifier()

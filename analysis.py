#!/usr/bin/env python
import nltk
import json

def main(*args):
    posts_dict = get_data()
    labels_dict = {}
    for label in posts_dict["label"]:
        if label in labels_dict.keys():
            labels_dict[label] = labels_dict[label] + 1
        else:
            labels_dict[label] = 1
    print(labels_dict)

def get_data():
    f = open("data.json", "r")
    json_string = f.read()
    dict = json.loads(json_string)
    return dict

if __name__ == "__main__":
    main()

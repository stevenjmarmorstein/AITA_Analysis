#! usr/bin/env python3

# Author: Steven Marmorstein
# Uses the PRAW API to get the top 1000 AITA posts and label them accordingly
# before writing the data to a file called data.json which is composed of a
# dictionary of three lists : title, body, and label where the ith entry corresponds
# to the ith title, body, and label annotated.
import praw
import pandas as pd
import datetime as dt
import json


PERSONAL_USE_SCRIPT_14_CHARS = input("enter PERSONAL_USE_SCRIPT_14_CHARS:")
SECRET_KEY_27_CHARS = input("enter SECRET_KEY_27_CHARS:")
APP_NAME = 'Data'
USERNAME = input("enter USERNAME:")
PASSWORD = input("enter PASSWORD:")
SUBREDDIT_NAME = 'AmItheAsshole'

def main():
    # Praw provides the API for accessing reddit:

    reddit = praw.Reddit(client_id=PERSONAL_USE_SCRIPT_14_CHARS, \
                     client_secret=SECRET_KEY_27_CHARS, \
                     user_agent=APP_NAME, \
                     username=USERNAME, \
                     password=PASSWORD)
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    # Top_subreddit will contain the top 1000 submissions in the subreddit:
    top_subreddit = subreddit.top('all', limit=1000)
    posts_dict = { "title":[], "body":[], "label":[]}
    cnt_posts_labelled = 0
    for submission in top_subreddit:
        # Not adding updates or meta posts to the dataset since they do not contain judgements:
        if 'update' in submission.title.lower() or 'meta' in submission.title.lower():
            continue
        label = get_label(submission)
        if (label != None):
            posts_dict["title"].append(submission.title)
            posts_dict["body"].append(submission.selftext)
            posts_dict["label"].append(label)
            cnt_posts_labelled += 1

    # Writing the data to a file:
    with open("data.json", "w+") as outfile:
        json.dump(posts_dict, outfile)


    print("Number of posts successfully labelled:", str(cnt_posts_labelled))

def get_label(submission):
    label = get_label_from_flair(submission.link_flair_text)
    if (label != None):
        return label
    else:
    # Getting the comments for this submission
        top_comments = get_top_comments(submission)

        i = 0
        if(label != ''):
            label = 'r'
            while(label == 'r'):
                pos_judgement = top_comments[i].body[0:3].upper()
                if pos_judgement.upper() == 'NTA':
                    return 'NTA'
                elif pos_judgement.upper() == 'YTA':
                    return 'YTA'
                elif pos_judgement.upper() == 'ESH':
                    return 'ESH'
                elif pos_judgement.upper() == 'NAH':
                    return 'NAH'
                else:
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    # Case where user has to answer:
                    # Print the title:
                    if (i == 0):
                        print(submission.title, '\n')
                        print(top_comments[i].body, '\n')
                        label = input("1. NTA\n2. YTA \n3. ESH\n4. NAH\n5. INFO\n")
                    else:
                        print(top_comments[i].body, '\n')
                        label = input()

                    i = i+1
                    next_top_comment = top_comments[i]
                    if label == '1':
                        return 'NTA'
                    elif label == '2':
                        return 'YTA'
                    elif label == '3':
                        return 'ESH'
                    elif label == '4':
                        return 'NAH'
                    elif label == '5':
                        return 'INFO'
                    elif label == 'r':
                        continue
                    else:
                        return None

def get_label_from_flair(flair):
    if(flair == "Not the A-hole"):
        return "NTA"
    elif(flair == "Asshole"):
        return "YTA"
    elif(flair == "Everyone Sucks"):
        return "ESH"
    elif(flair == "No A-holes here"):
        return "NAH"
    elif(flair == "Not enough info"):
        return "INFO"
    else:
        return None

def get_top_comments(submission, limit=10):
    submission.comment_sort = 'top'
    comments = submission.comments.list()
    return comments[:limit]

if __name__ == '__main__':
    main()

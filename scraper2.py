# Author: Steven Marmorstein

import pandas as pd
import requests
import json
import csv
import time
from datetime import datetime, timedelta
import praw

def main(*args):
    # Gets a list of all submission ids that will be mined for data:
    annotator()
    # print(data[sub_idx])
    # for key in data[sub_idx].keys():
    #     print(key, data[sub_idx][key])
    # print(data[sub_idx]['score'])
    # print(data[sub_idx]['title'])
    # print(data[sub_idx]['author_flair_text'])
    # print(data[sub_idx]['selftext'])
    # reddit = get_praw_reddit()
    # subm = praw.models.Submission(reddit, id=data[sub_idx]['id'], url=None, _data=None)
    # print(subm.title)
    # print(subm.score)
    # print(len(data))

def annotator():
    """
    Takes a list of submission ids and writes a JSON file with a dictionary
    containing three lists: title, body, and label where the ith entry corresponds
    to the ith title, body, and label annotated.
    """

    reddit = get_praw_reddit()
    submissions = get_submissions(reddit)
    posts_dict = { "title":[], "body":[], "label":[]}
    cnt_posts_labelled = 0
    # TODO: Batch the submissions so the annotator isn't waiting.
    for subm in submissions:
        label = get_label(subm)
        if (label != None):
            posts_dict["title"].append(subm.title)
            posts_dict["body"].append(subm.selftext)
            posts_dict["label"].append(label)
            cnt_posts_labelled += 1

    # Writing the data to a file:
    filename = "big_data.json"
    with open(filename, "w+") as outfile:
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
        # Skips the mod's pinned comment about the comments:
        if "If you want your comment to count toward judgment," in top_comments[i].body:
            i = 1
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
                elif "Your post has been removed." in top_comments[i].body:
                    return None
                else:
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    # Case where user has to answer:
                    # Print the title:
                    print(submission.title, '\n')
                    print(top_comments[i].body, '\n')
                    label = input("1. NTA\n2. YTA \n3. ESH\n4. NAH\n5. INFO\n")
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


def get_top_comments(submission, limit=15):
    """
    Returns a list of the top PRAW comment objects of a PRAW submission. Default
    is top ten, but limit can be changed to increase the number of required
    comments.
    """
    submission.comment_sort = 'top'
    comments = submission.comments.list()
    return comments[:limit]


def get_submissions(reddit):
    """
    Returns a list of PRAW submissions, filtering out updates, and meta posts.
    Takes a single instance of PRAW reddit as an argument.
    """
    subm_ids = get_subm_ids()
    submissions = []
    for subm_id in subm_ids:
        submission = reddit.submission(subm_id)
        # Confirms that the submission request was successful:
        try:
            # Not adding updates or meta posts to the dataset since they do not contain judgements:
            if 'update' in submission.title.lower() or 'meta' in submission.title.lower():
                continue
            else:
                submissions.append(submission)
        except:
            continue

    return submissions

def get_subm_ids():
    """
    Returns a list of submission ids as strings, accumulating as many posts as
    possible from the AITA subreddit.
    """

    # Size of the intervals that are queried:
    step_size = 7

    # Initializing data:
    before_date = datetime.today()
    after_date = before_date - timedelta(days=step_size)
    data = get_data(before_date, after_date)

    count_ids = 0
    ids_list = []
    while len(data) != 0:
        count_ids += len(data)
        print(len(data))
        for i in range(len(data)):
            ids_list.append(data[i]['id'])
        before_date = after_date
        after_date = before_date - timedelta(days=step_size)
        data = get_data(before_date, after_date)

    print(count_ids)
    return ids_list


def get_data(before_date, after_date):
    """
    Takes two datetime objects (before_date and after_date) and returns a list
    of up to 1000 dictionaries of posts from r/AITA with the dictionaries having
    entries corresponding to the pushshift.io submission search structure. There
    is a score minimum that is used to ensure that all saved judgements come from
    a collective and not an anomalous first or only comment and that low-effort
    posts are weeded out. Returns an empty list if there is no data.
    """

    # Name of the subreddit to scrape:
    sub = "AmITheAsshole"
    # Only returns posts with scores >= the limit
    score_limit = 80
    # Getting the offsets:
    before_date_offset = str(before_date.timestamp())[0:10]
    after_date_offset = str(after_date.timestamp())[0:10]
    url = 'https://api.pushshift.io/reddit/search/submission/?size=1000&subreddit=' \
    + str(sub) + "&before=" + before_date_offset + "&after=" + after_date_offset + "&sort_type=score&score=>" + str(score_limit)

    # Making the request of the pushshift.io API
    r = requests.get(url)
    # returns empty list if request was unsuccessful
    try:
        data = json.loads(r.text)
        return data['data']
    except:
        return []

def get_praw_reddit():
    """
    Gets reddit bot credentials (from the user) to instantiate and return a PRAW
    reddit instance.
    """
    PERSONAL_USE_SCRIPT_14_CHARS = input("enter PERSONAL_USE_SCRIPT_14_CHARS:")
    SECRET_KEY_27_CHARS = input("enter SECRET_KEY_27_CHARS:")
    APP_NAME = 'Data'
    USERNAME = input("enter USERNAME:")
    PASSWORD = input("enter PASSWORD:")
    SUBREDDIT_NAME = 'AmItheAsshole'
    reddit = praw.Reddit(client_id=PERSONAL_USE_SCRIPT_14_CHARS, \
                     client_secret=SECRET_KEY_27_CHARS, \
                     user_agent=APP_NAME, \
                     username=USERNAME, \
                     password=PASSWORD)
    return reddit


if __name__ == "__main__":
    main()

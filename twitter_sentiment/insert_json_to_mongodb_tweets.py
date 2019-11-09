# coding:utf-8

import os
import json
from bson import json_util
import sys, json, pymongo
from pymongo import MongoClient
from typing import Any

def json_read_and_insertDB(path):
    file_list = os.listdir(path)
    file_list.pop(2) # bag fix
    print(file_list)
    for filename in file_list:
        collection = db[f"{filename}_db"]
        print(filename, collection)
        with open(path + os.sep + filename, 'r', encoding='utf8') as data_file:
            for line in data_file:
                data_json = json.loads(line)
                collection.insert_one(data_json)
    return
if __name__ == "__main__":
    path = '../twitter'
    connection = MongoClient('localhost', 27017)
    db = connection["tweets_data"]  # type
    json_read_and_insertDB(path)
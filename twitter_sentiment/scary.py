# -*- coding: utf-8 -*-
import MeCab
import pandas as pd
import numpy as np
import mongo_to_xls_API_big as monrad
import preprocess as pp

def flatten(nested_list):
    """2重のリストをフラットにする関数"""
    return [e for inner_list in nested_list for e in inner_list]
texts = monrad.li
x=[]

def returned():
    keywords=[]
    f = open("../input/scary.txt", "r", encoding="utf-8")
    keyword = f.read()
    f.close()
    keywords.append(keyword.split('\n'))
    return keywords

def matching_scary(keyword,texts):
    i = []
    for text in texts:
        for k in key:
            if line.find(k) > 0:
                text = pp.normalize_neologd(line)
                i.append(text)
                break
            else:
                continue
    result = pd.Series(i)
    return result

if __name__ == "__main__":
    texts = monrad.li
    key = flatten(returned())
    result = matching_scary(key,texts)
    #output_Excelsheet
    result.to_excel("shitehoshii_result.xls")
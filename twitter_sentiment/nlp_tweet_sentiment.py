#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import re
import csv
import json
import MeCab
from bs4 import BeautifulSoup
import codecs
#import scary as pp
import urllib


# 名詞評価極性辞書を読み込む
in_file = csv.reader(open('../input/pn.txt', "r"))
pne = []
for line in in_file:
    try:
        if line[1] == 'p':
            score = 1.0
        elif line[1] == 'e':
            score = 0.0
        elif line[1] == 'n':
            score = -1.0
        pne.append((line[0], score))
    except:
        pass
in_file = csv.reader(open('../input/pnverb.txt', "r"))
for line in in_file:
    try:
        if line[0] == 'ポジ':
            score = 1.0
        elif line[0] == 'ネガ':
            score = -1.0
        pne.append((line[0], score))
    except:
        pass

# トークンのリストのP/Nを判定する。
def judge_pn(tokens):
    score = 0
    num_score = 0
    for token in tokens:
        for _pne in pne:
            if token == _pne[0]:
                score += _pne[1]
                num_score += 1
    if num_score != 0:
        pn_rate = float(score) / float(num_score)
    else:
        pn_rate = 0.5

    return pn_rate

# 文章をmecabで分かちがきして、名詞・動詞・形容詞の単語一覧を返す
def wakati(text):
    result = []
    tagger = MeCab.Tagger()
    #text = text.encode("utf-8")
    tagger.parse('')
    node = tagger.parseToNode(text)#parseToNodeは分かち書きの詳細を表示する
    # 助詞や助動詞は拾わない
    while node is not None:
        # 品詞情報取得
        # Node.featureのフォーマット：品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
        hinshi = node.feature.split(",")[0]
        hinshi2 = node.feature.split(",")[1]
        if hinshi in ["名詞"]:
            if hinshi2 not in ["数", "接尾", "記号", "サ変接続", "*"]:
            # 表層形の取得、単語の文字が入ってる、いらない単語除去
                if node.surface not in ['ん','-','ー','w','の','www','い','とこ', 'ア', 'ノミ', 'ス','g','ぁぁぁ','ゎ','ぱ','ざ','wh','wl','fujitv','こ','す']:
                    result.append(node.surface)
        elif hinshi in ["形容詞"]:
            # 形態素情報から原形情報取得
            result.append(node.feature.split(",")[6])
        node = node.next
    return u" ".join(result)

# 個々のツイート本文をトークン化
def tokenize_list(texts):
    sents = []
    for text in texts:
        if re.search(u"放射線", text) or re.search(u"被爆", text) or re.search(u"被曝", text) or re.search(u"被ばく", text):
            tokenized_text = wakati(text)
            sents.append((text, tokenized_text))
    print(sents[0][0],sents[0][1])
    print(sents[1][0], sents[1][1])
    print(sents[2][0], sents[2][1])
    return sents

# 個々のツイート本文のP/Nを判定し、pn_ratesに格納
def pn_rates_and_sents(sents):
    pn_rates = []
    pn_rates_with_sents = []
    for sent in sents:
        pn_rate = judge_pn(sent[1])
        pn_rates.append(pn_rate)
        pn_rates_with_sents.append((sent[0], pn_rate))
    return pn_rates, pn_rates_with_sents

# P/E/Nスコアを算出して出力する
def print_scores(pn_rates):
    p, e, n = 0.0, 0.0, 0.0
    p_num, e_num, n_num = 0.0, 0.0, 0.0
    for pn in pn_rates:
        if pn > 0.5:
            p += pn
            p_num += 1
        elif pn == 0.5:
            e += pn
            e_num += 1
        elif pn < 0.5:
            n += pn
            n_num += 1
    sum = p_num + e_num + n_num


if __name__ == '__main__':

    with codecs.open("./tweets_.csv", 'r', 'utf-8') as f:
        text_lists = []
        for line in f:
            line = line.replace("\n", "")
            text_lists.append(line)
    t = text_lists
    sents = tokenize_list(t)
    pn_rates, pn_rates_with_sents = pn_rates_and_sents(sents)

    result = []
    for pn_rate_with_sent in pn_rates_with_sents:
        if pn_rate_with_sent[1] <= -0.3:
            result.append(pn_rate_with_sent[0])
        else:
            pass

    with open("./pn-0.3.csv", 'w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')  # 改行コード（\n）を指定しておく
        for text in result:
            t = [text]
            writer.writerow(t)

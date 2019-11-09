# -*- coding: utf-8 -

import MeCab
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

import codecs
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy import genfromtxt

import os
import urllib.request
import preprocess as pp

def download_stopwords(path):
    url = 'http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt'
    if os.path.exists(path):
        print('File already exists.')
    else:
        print('Downloading...')
        # Download the file from `url` and save it locally under `file_name`:
        urllib.request.urlretrieve(url, path)

def create_stopwords(file_path):
    stop_words = []
    for w in open(path, "r"):
        w = w.replace('\n','')
        if len(w) > 0:
          stop_words.append(w)
    return stop_words

# 文章をmecabで分かちがきして、名詞・動詞・形容詞の単語一覧を返す
def wakati(text):
    tagger = MeCab.Tagger()
    #text = text.encode("utf-8")
    tagger.parse('')
    node = tagger.parseToNode(text)#parseToNodeは分かち書きの詳細を表示する
    result = []
    # 助詞や助動詞は拾わない
    while node is not None:
        # 品詞情報取得
        # Node.featureのフォーマット：品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
        hinshi = node.feature.split(",")[0]
        hinshi2 = node.feature.split(",")[1]
        if hinshi in ["名詞"]:
            if hinshi2 not in ["数", "接尾", "記号", "サ変接続", "*"]:
            # 表層形の取得、単語の文字が入ってる
                if node.surface not in ['ん','-','ー','w','の','www','い','とこ', 'ア', 'ノミ', 'ス','g','ぁぁぁ','ゎ','ぱ','ざ','wh','wl','fujitv','こ','す']:
                    result.append(node.surface)
        elif hinshi in ["形容詞"]:
            # 形態素情報から原形情報取得
            result.append(node.feature.split(",")[6])
        node = node.next
    return u" ".join(result)

def removeStoplist(documents, stoplist):
	u"""ストップワードを取り除く"""
	stoplist_removed_documents = []
	for document in documents:
		words = []
		for word in document.lower().split():
			if word not in stoplist:
				words.append(word)
		stoplist_removed_documents.append(words)
	return stoplist_removed_documents

def getTokensOnce(all_tokens):
	u"""一回しか出現しない単語を返す"""
	tokens_once = set([])
	for word in set(all_tokens):
		if all_tokens.count(word) == 1:
			tokens_once.add(word)
	return tokens_once

def removeTokensOnce(documents, tokens_once):
	u"""一回しか出現しない単語を取り除く"""
	token_removed_documents = []
	for document in documents:
		words = []
		for word in document:
			if word not in tokens_once:
				words.append(word)
		token_removed_documents.append(words)
	return token_removed_documents

def show_cluster(corpus):
    vectorizer = CountVectorizer(token_pattern=u'(?u)\\b\\w+\\b')
    transformer = TfidfTransformer()

    tf = vectorizer.fit_transform(corpus)
    tfidf = transformer.fit_transform(tf)

    km_model = KMeans(n_clusters=3)
    km_model.fit(tfidf)
    dim = 3
    if dim == 3:
        lsa = TruncatedSVD(dim)
        compressed_text_list = lsa.fit_transform(tfidf)
        compressed_center_list = lsa.fit_transform(km_model.cluster_centers_)
        compressed_text_df = pd.DataFrame(columns=['x', 'y', 'z', 'cluster'])

        for num in range(len(compressed_text_list)):
            temp_df = pd.DataFrame({'x': compressed_text_list[num][0],
                                    'y': compressed_text_list[num][1],
                                    'z': compressed_text_list[num][2],
                                    'cluster': [km_model.labels_[num]]})
            compressed_text_df = compressed_text_df.append(temp_df, ignore_index=True)
        fig = plt.figure()
        ax = Axes3D(fig)
        for key, data in compressed_text_df.iterrows():
            if data[3] == 1:
                ax.scatter(data[0], data[1], data[2], c='b', label=data[3])
            elif data[3] == 2:
                ax.scatter(data[0], data[1], data[2], c='r', label=data[3])
            elif data[3] == 0:
                ax.scatter(data[0], data[1], data[2], c='c', label=data[3])
            # elif data[3]==3:
            #     ax.scatter(data[0], data[1], data[2], c='m', label=data[3])
        plt.show()
        plt.close()
    return

def output_df(text_df, compressed_text_df):
    vectorizer = CountVectorizer(token_pattern=u'(?u)\\b\\w+\\b')
    transformer = TfidfTransformer()

    tf = vectorizer.fit_transform(corpus)
    tfidf = transformer.fit_transform(tf)

    km_model = KMeans(n_clusters=3)
    km_model.fit(tfidf)
    dim = 3
    if dim == 3:
        lsa = TruncatedSVD(dim)
        compressed_text_list = lsa.fit_transform(tfidf)
        compressed_center_list = lsa.fit_transform(km_model.cluster_centers_)
        compressed_text_df = pd.DataFrame(columns=['x', 'y', 'z', 'cluster'])

        for num in range(len(compressed_text_list)):
            temp_df = pd.DataFrame({'x': compressed_text_list[num][0],
                                    'y': compressed_text_list[num][1],
                                    'z': compressed_text_list[num][2],
                                    'cluster': [km_model.labels_[num]]})
            compressed_text_df = compressed_text_df.append(temp_df, ignore_index=True)
    text_df = pd.concat([text_df, compressed_text_df], axis=1)
    return text_df

def output_cluster(text_df,file):
    text_list0=[]
    text_list1=[]
    text_list2=[]
    for text in text_df[text_df['cluster']==0].texts:
        text_list0.append(text)
    with open(f"./{file}_0.txt", 'wt') as f:
        f.write('\n'.join(text_list0))

    for text in text_df[text_df['cluster']==1].texts:
        text_list1.append(text)
    with open(f"./{file}_1.txt", 'wt') as f:
        f.write('\n'.join(text_list1))

    for text in text_df[text_df['cluster']==2].texts:
        text_list2.append(text)
    with open(f"./{file}_2.txt", 'wt') as f:
        f.write('\n'.join(text_list2))
    return

if __main__ == "__name__":
    file = 'hogehoge'
    text_df = pd.read_csv(f"./{file}_nb.csv",encoding='utf-8')
    wakatigaki = []
    for text in text_df['texts']:
        text = pp.normalize_neologd(text)
        text = ''.join(text)
        text = wakati(text)
        wakatigaki.append(text)
    texts = removeStoplist(wakatigaki, stop_words)
    all_tokens = sum(texts,[])
    tokens_once = getTokensOnce(all_tokens)
    texts = removeTokensOnce(texts,tokens_once)

    with open(f"./{file}_nb_vector.txt", 'wt') as f:
        writer = csv.writer(f)
        writer.writerows(texts)

    # データの用意
    corpus = codecs.open(f'./{file}_nb_vector.txt', 'r', 'utf-8').read().splitlines()
    output_cluster()
    output_df()
    show_cluster()
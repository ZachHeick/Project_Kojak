import boto3
import random
import os
import pandas as pd
import pickle
import nltk
from nltk.corpus import stopwords
from nltk import RegexpTokenizer
from gensim.models import doc2vec
from collections import namedtuple

# Get Lyrics Dataframe from S3
s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET_KEY'])
s3.download_file('metis-project-kojak-bucket', 'all_lyrics_dataframe.pickle', 'all_lyrics_dataframe.pickle')

print('Downloaded lyrics dataframe')

with open('all_lyrics_dataframe.pickle', 'rb') as f:
    df = pickle.load(f)

# Pre-processing
tokenizer = RegexpTokenizer(r'\w+')
stopword_set = set(stopwords.words('english'))

def get_clean_lyrics(documents):
    clean_lyrics = []
    for document in documents:
        lines = document.lower().split('\n')
        tokenized_lines = []
        for line in lines:
            if line != '' and line[-1] != ':':
                tokens = tokenizer.tokenize(line.lower())
                song_tokens = []
                for token in tokens:
                    if len(token) >= 1 and token != '' and token not in stopword_set:
                        if token[-3:] == 'in\'':
                            token += 'g'
                        song_tokens.append(token)
                tokenized_lines += song_tokens
        clean_lyrics.append(tokenized_lines)
    return clean_lyrics

clean_lyrics = get_clean_lyrics(df['lyrics'])

print('Lyrics cleaned')

# Train Song2vec
class LabeledLineSentence():
    def __init__(self, doc_list):
        self.doc_list = doc_list

    def to_array(self):
        self.labeled_doc_list = []
        for i, doc in enumerate(self.doc_list):
            self.labeled_doc_list.append(doc2vec.LabeledSentence(doc, [i]))
        return self.labeled_doc_list

    def shuffle_docs(self):
        random.shuffle(self.labeled_doc_list)
        return self.labeled_doc_list

LLS = LabeledLineSentence(clean_lyrics)
model = doc2vec.Doc2Vec(size = 100, window = 12, min_count = 1, workers = 64)
model.build_vocab(LLS.to_array())

print('Training model...')

model.train(LLS.shuffle_docs(), total_examples=model.corpus_count, epochs=100)

print('Model trained')

model.save('song2vec_model_v2')
s3.upload_file('song2vec_model_v2', 'metis-project-kojak-bucket', 'song2vec_model_v2')

print('Model saved and uploaded')

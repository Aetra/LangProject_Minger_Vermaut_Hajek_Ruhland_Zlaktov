import nltk
import FichiersXml
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import displayfunction
# coding: utf-8

sentence = [("the", "DT"), ("little", "JJ"), ("yellow", "JJ"),  ("dog", "NN"), ("barked", "VBD"), ("at", "IN"),  ("the", "DT"), ("cat", "NN")]

grammar = "NP: {<DT>?<JJ>*<NN>}"

cp = nltk.RegexpParser(grammar)
result = cp.parse(sentence)
print(result)

def ie_preprocess(AmeliaDyer):
    sentences = nltk.sent_tokenize(AmeliaDyer)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]

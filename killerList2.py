import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import displayfunction
# coding: utf-8

from lxml import etree

tree = etree.parse("data.xml")
for user in tree.xpath("/users/user/nom"):
    print(user.text)

# charger le texte dans python
text1 = """The decision by the independent MP Andrew Wilkie to withdraw his 
            support for the minority Labor government sounded dramatic but 
            it should not further threaten its stability. When, after the 
            2010 election, Wilkie, Rob Oakeshott, Tony Windsor and the
            Greens agreed to support Labor, they gave just two guarantees: 
            confidence and supply."""

# écrire la fonction qui tokenise et qui applique part of speech tagging
def preprocess(doc):
    doc = nltk.word_tokenize(doc)
    doc = nltk.pos_tag(doc)
    return doc

print(text1)
text = preprocess(text1)
print(text)
print(len(text1))

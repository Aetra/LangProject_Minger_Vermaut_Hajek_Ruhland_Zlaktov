# -*- coding: utf-8 -*-
from lxml import html
from lxml import etree
import nltk
from testValide import isALocation

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def recuperationText(path):
    # Entree : string qui est le chemin vers nos données XML
    # Sortie : l'objet de la balise soit un texte
    # Objectif : recuper un texte XML et le transformer en texte de string
    # Etape 1 : l'extraction des balise textes
    tree = etree.parse(path)  # c'est le dossier dans lequel on a du XML
    root = tree.getroot()  # permet de recuperer la racine
    childrenRoot = root.getchildren()
    liste = []
    for rdc in childrenRoot:
        for etage in rdc:
            # print(elt1.getchildren())
            captureText = etage.findall("{http://www.mediawiki.org/xml/export-0.10/}text")  # captureText est une liste
            for textBalise in captureText:
                liste.append(textBalise.text)

    # Etape 2 : transformer la liste de texte en super texte
    megaText = " ".join(liste)

    # Renvoie le texte
    return megaText


# return list of sentences
def purge(doc):
    result = "";
    flag = True;

    for mot in doc:

        # on enlève les contenues informatiques du style {%fbhjeiud} ou <ref></ref>
        if mot == '{' or mot == '<':
            flag = False;
        elif mot == '}' or mot == '>':
            flag = True;
        elif flag:

            if (mot not in ['\'', '[', ']', '=', '|', '*']):
                result += mot;

            # on retire ensuite les ponctuations inutiles
            # if mot not in [ ';' , ':' , '\'']:

    # le texte est enfin "nettoyé"
    # print(result)
    sentences = result.split('\n')
    return sentences


def secondPurgeAndTokenize(list_of_sentences):
    tok_sentences = []
    for s in list_of_sentences:
        # delete the empty lines and tokenize the sentences
        if len(s) > 0:
            tok_sentences.append(nltk.word_tokenize(s))
    return tok_sentences


# In[309]:


def sortByCountries(
        list_tok_sentences):  # takes a list of tokenized sentences and return a dictionnary with cases indexed by countries
    liste = []
    index = 'none'
    dicti = {}
    for t in list_tok_sentences:
        # we store murder cases in a temporary list
        # we make a semantic test to check if the expression is not a location (country, city...)
        # In our corpus murders are presented by countries, so if we find a new single counrty name (like 'The Bahamas')
        # it means we have now the murders in Bahamas, so we store our list of murder in the dictionnary,
        # indexed with the country which came before and we empty the list
        if isALocation('_'.join(t)):
            # if the country is already in the list
            if index in dicti:
                dicti[index].extend(liste)
            else:
                dicti[index] = liste
            liste = []
            index = ' '.join(t)
        else:
            liste.append(t)
    # we delete the introduction of the corpus (everything written before the first country)
    del dicti['none']
    return dicti

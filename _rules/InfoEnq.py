import nltk
from _planning.CleanProcess import fctKillerList, cleanDoub, getTextForEnq, cleanText
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import _rules.RulesChunk


#On retourne le texte de la page wikipedia pour notre enquête
def getText(cdtTp):
    killer_list = fctKillerList()
    all_text = []
    for killer in killer_list:
        containInfo, text = getTextForEnq(killer[1])
        if cdtTp:
            all_text.append((killer[0], cleanText(text)))
        else:
            all_text.append((killer, text))
    return all_text

#retourne true si on trouve un synonyme verbe tuée
def boolMurderVb(sentence):
    lemmatizer = WordNetLemmatizer()
    murderSyn = [w.lemma_names()[0] for w in wn.synsets(lemmatizer.lemmatize('murder', pos="v"))]
    tokens = nltk.word_tokenize(sentence)
    for t in tokens:
        if lemmatizer.lemmatize(t, pos="v") in murderSyn:
            return True
    return False

#On retourne true si on trouve un synonyme du nom murder
def boolMurderNom(sentence):
    lemmatizer = WordNetLemmatizer()
    syn_murder = [w.lemma_names()[0] for w in wn.synsets(lemmatizer.lemmatize('murder'))]
    tokens = nltk.word_tokenize(sentence)
    for t in tokens:
        if lemmatizer.lemmatize(t, pos="n") in syn_murder:
            return True
    return False

#on retourne les phrases comprenant un synonyme du verbe murder
def getMurderVb(text):
    sentences = _rules.RulesChunk.tokenizePhrase(text[1])
    usefull_sentences = []
    for sentence in sentences:
        if boolMurderVb(sentence):
            usefull_sentences.append(sentence)
    return usefull_sentences

#on retourne les phrases contenant un synonyme du nom murder
def getMurderNom(text):
    sentences = _rules.RulesChunk.tokenizePhrase(text[1])
    usefull_sentences = []
    for sentence in sentences:
        if boolMurderNom(sentence):
            usefull_sentences.append(sentence)
    return usefull_sentences

#on retourne le contenu du nombre de victimes tuèes par le killer en associant les régles pour obtenir la localisation, le nom de la victimee
def getNbVictims(text):
    chunks = _rules.RulesChunk.process_content(text)
    victims = []
    for chunk in chunks:
        victims = victims + _rules.RulesChunk.murderIndivVb(chunk) + _rules.RulesChunk.murderIndivNom(chunk) + _rules.RulesChunk.murderLocNom(chunk)[0]
    killer = text[0]
    victims = set(victims)
    to_remove = []
    for x in victims:
        if killer in x or x in killer:
            to_remove.append(x)
    for x in to_remove:
        victims.remove(x)
    return cleanDoub(victims)

#On retourne la date du meurtre associé
def getDates(text):
    chunks = _rules.RulesChunk.process_content(text)
    dates = []
    for chunk in chunks:
        dates = dates + _rules.RulesChunk.murderDates(chunk)
    dates = set(dates)
    return cleanDoub(dates)

#On retourne la localisation du meurtre associé
def getLieu(text):
    chunks = _rules.RulesChunk.process_content(text)
    places = []
    for chunk in chunks:
        places = places + _rules.RulesChunk.murderLocNom(chunk)[1]
    places = set(places)
    return cleanDoub(places)


#On retourne la victime et la date ensemble, sous forme de tuple victime-date
def getDateVic(text):
    chunks = _rules.RulesChunk.motifChunk(text)
    vicDate = []
    for chunk in chunks:
        info = _rules.RulesChunk.murderVictDates(chunk)
        if info != None:
            vicDate.append(_rules.RulesChunk.murderVictDates(chunk))
    return vicDate

import re

from _planning.CleanProcess import fctKillerList, getTextForEnq
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

#On récupère le xml pour transformer en text et poursuivre le travail de nettoyage
killerList = fctKillerList()


#Renvoie une liste contenant toutes les informations sur le killer, on rajoute au bout les informations
def getAllInfo():
    infoKiller = []
    for killer in killerList:
        infobox, text = getTextForEnq(killer[1])
        infoKiller.append((killer, infobox))
    return infoKiller

#On utilise les lemmes pour ranger corectement nos informations récupérés
lemmatizer = WordNetLemmatizer()
syn_name = [w.lemma_names()[0] for w in wn.synsets(lemmatizer.lemmatize('name'))] + ['name']
syn_victims = [w.lemma_names()[0] for w in wn.synsets(lemmatizer.lemmatize('victims'))] + ['victims']
syn_place = [w.lemma_names()[0] for w in
             wn.synsets(lemmatizer.lemmatize('place')) + wn.synsets(lemmatizer.lemmatize('country'))] + ['City'] + ['country'] + [
                'states']

#On met bout à bout avec ce qu'on a utilisé au préalables les informations, on gére doublon ect pour avoir un rendu propre
def begin_research_infobox(killerInfo):
    enqueteur = [[], [], [], [], [], [],
                 []]  # nom du tueur, victimes, lieux, date début, date fin, [dates seules], (duo info: nom, date)
    txt = killerInfo.replace("|", "")
    tokens = txt.split("\n")[1:]
    tabInfo = []
    for t in tokens:
        if '=' in t:
            if t[0] == " ":
                t = t[1:]
            info = t.split('=')
            if info[1] != "nbfrerez" and info[1] != " " and info[1 != "\n"]:
                info[0] = info[0].strip()
                info[1] = info[1].strip()
                tabInfo.append(info)
    for info in tabInfo:
        if info[0] in syn_name:
            enqueteur[0].append(info[1])
        elif info[0] in syn_victims:
            enqueteur[1].append(info[1])
        elif info[0] in syn_place:
            enqueteur[2].append(info[1])
    return enqueteur

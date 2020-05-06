import nltk
import re

from _planning.CleanProcess import cleanText
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import _rules.InfoEnq

#on peut diviser la la phrase en mots utilisation de la librairie nltk
def tokenizePhrase(txt):
    token = nltk.sent_tokenize(cleanText(txt))
    return token


#On Renvoie les groupes de mots contenant le motif <IN>*?<NNP>*?<VB.?|NN|NNP|DT>+<IN>*?<...?.?>*?<NNP|CD>+<NN>*?
def process_content(text):
    sentences = set(_rules.InfoEnq.getMurderVb(text) + _rules.InfoEnq.getMurderNom(text))
    chunk = []
    try:
        for sentence in sentences:
            sentence = re.sub(',', '', sentence)
            words = nltk.word_tokenize(sentence)
            tagged = nltk.pos_tag(words)
            ne = nltk.ne_chunk(tagged, binary=False)
            chunk_gram = r"""Chunk: {<VB.?|NN|NNP|DT>+<IN>*?<...?.?>*?<NNP|CD>+<NN>*?}"""
            chunkParser = nltk.RegexpParser(chunk_gram)
            chunked = chunkParser.parse(tagged)
            for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Chunk'):
                chunk.append(subtree)
    except Exception as e:
        print(e)
    return chunk

#On recherche si on a un synonyme du verbe murder pour l'individu et on le retourne
def murderIndivVb(chunk):
    nomP = []
    chunk_gram = r"""Verb: {<VB.?>}"""
    chunkParser = nltk.RegexpParser(chunk_gram)
    chunked = chunkParser.parse(chunk)
    chunks = []
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Verb'):
        chunks.append(subtree)
    if chunks != []:
        verb = chunks[0][0][0]
        lemmatizer = WordNetLemmatizer()
        syn_murder = set([w.lemma_names()[0] for w in wn.synsets(lemmatizer.lemmatize('murder', pos="v"))])
        if lemmatizer.lemmatize(verb, pos="v") in syn_murder:
            tagged = nltk.ne_chunk(chunk, binary=False)
            for ne in tagged.subtrees():
                if ne.label() == 'PERSON':
                    person = ""
                    for node in ne:
                        person = person + " " + node[0]
                    nomP.append(person[1:])
    return nomP

#On cherche si on à un synonyme du nom murder pour l'entité  et on le retourne
def murderIndivNom(chunk):
    nomP = []
    chunk_gram = r"""Murder: {<NN|NNS><IN>}"""
    chunkParser = nltk.RegexpParser(chunk_gram)
    chunked = chunkParser.parse(chunk)
    chunks = []
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Murder'):
        chunks.append(subtree)
    if chunks != []:
        noun = chunks[0][0][0]
        lemmatizer = WordNetLemmatizer()
        syn_murder = set([w.lemma_names()[0] for w in wn.synsets(lemmatizer.lemmatize('murder', pos="n"))])
        if lemmatizer.lemmatize(noun, pos="n") in syn_murder:
            tagged = nltk.ne_chunk(chunk, binary=False)
            for ne in tagged.subtrees():
                if ne.label() == 'PERSON':
                    person = ""
                    for node in ne:
                        person = person + " " + node[0]
                    nomP.append(person[1:])
    return nomP


#On retrouve le lieu du meurtre en prenant un synonyme du nom meutre puis une préposition pour ensuite avoir une localisation retourné
def murderLocNom(chunk):
    nomP = []
    places = []
    chunk_gram = r"""Murder: {<NN|NNS><IN>}"""
    chunkParser = nltk.RegexpParser(chunk_gram)
    chunked = chunkParser.parse(chunk)
    chunks = []
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Murder'):
        chunks.append(subtree)
    if chunks != []:
        noun = chunks[0][0][0]
        prep = chunks[0][1][0]
        lemmatizer = WordNetLemmatizer()
        syn_murder = set([w.lemma_names()[0] for w in wn.synsets(lemmatizer.lemmatize('murder', pos="n"))])
        if lemmatizer.lemmatize(noun, pos="n") in syn_murder:
            tagged = nltk.ne_chunk(chunk, binary=False)
            for ne in tagged.subtrees():
                if ne.label() in ['GPE', 'LOC']:
                    if prep == 'of':
                        person = ""
                        for node in ne:
                            person = person + " " + node[0]
                        nomP.append(person[1:])
                    else:
                        place = ""
                        for node in ne:
                            place = place + " " + node[0]
                        places.append(place[1:])
    return nomP, places

#On retrouve la date du meurtre en prenant un synonyme du nom meutre puis une préposition pour ensuite avoir une localisation retourné, on le renvoie si contient un nombre équivalent à 4 chiffres ex(1998)
# Analyse un chunk pour y trouver des dates: cherche les cardinaux (CD) et éventuellement les noms propres (NNP),
# si le chunk contient au moins un nombre à 4 chiffres alors il est renvoyé
def murderDates(chunk):
    dates = []
    chunk_gram = r"""Murder: {<NN|NNS><IN><NNP>?<CD>+<CC>?<IN>?<NNP>?<CD>?}"""
    chunkParser = nltk.RegexpParser(chunk_gram)
    chunked = chunkParser.parse(chunk)
    chunks = []
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Murder'):
        chunks.append(subtree)
    if chunks != []:
        noun = chunks[0][0][0]
        lemmatizer = WordNetLemmatizer()
        syn_murder = set([w.lemma_names()[0] for w in wn.synsets(lemmatizer.lemmatize('murder', pos="n"))])
        if lemmatizer.lemmatize(noun, pos="n") in syn_murder:
            chunkForDate = r"""Date: {<IN>?<NNP>?<CD>+<CC>?<IN>?<NNP>?<CD>?}"""
            chunkParser_date = nltk.RegexpParser(chunkForDate)
            chunked_date = chunkParser_date.parse(chunk)
            chunks_date = []
            for subtree in chunked_date.subtrees(filter=lambda t: t.label() == 'Date'):
                chunks_date.append(subtree)
                if chunks_date != []:
                    date = ""
                    for x in subtree:
                        if x[1] in ['NNP', 'CD']:
                            date = date + " " + x[0]
                    if re.search("""(1|2|3|4|5|6|7|8|9|0){4}""", date[1:]) != None:
                        dates.append(date[1:])
    return dates


# On renvoie le chunck contenant <IN><NNP>*?<CD>+<NN|NNP|DT|PRP.?>+<VB.?><...?.?>*?<NN.?.?><IN>*?<...?.?>*?<NNP|CD>+<NN>*?
def motifChunk(text):
    sentences = set(_rules.InfoEnq.getMurderVb(text) + _rules.InfoEnq.getMurderNom(text))
    chunks = []
    try:
        for sentence in sentences:
            sentence = re.sub(',', '', sentence)
            words = nltk.word_tokenize(sentence)
            tagged = nltk.pos_tag(words)

            chunk_gram = r"""Chunk: {<IN><NNP>*?<CD>+<NN|NNP|DT|PRP.?>+<VB.?><...?.?>*?<NN.?.?><IN>*?<...?.?>*?<NNP|CD>+<NN>*?}"""

            chunkParser = nltk.RegexpParser(chunk_gram)
            chunked = chunkParser.parse(tagged)

            for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Chunk'):
                chunks.append(subtree)

    except Exception as e:
        print(e)
    return chunks

#On analyse le chunck pour retrouver une victime et une date associé
def murderVictDates(chunk):
    dates = []
    victimes = []
    chunkForDate = r"""Date: {<IN>?<NNP>?<CD>+}"""
    chunkVicVb = r"""Murder: {<VBD><PRP.?>?<JJ>?<NN>?<JJ>*<NNP>+}"""
    chunkVicNom = r"""Murder: {<NN><IN><PRP.?>?<JJ>?<NN.?>+}"""
    chunkParser = nltk.RegexpParser(chunkForDate)
    chunked = chunkParser.parse(chunk)
    tabChunkDate = []
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Date'):
        tabChunkDate.append(subtree)
        if tabChunkDate != []:
            date = ""
            for x in subtree:
                if x[1] in ['NNP', 'CD']:
                    date = date + " " + x[0]
            if re.search("""(1|2|3|4|5|6|7|8|9|0){4}""", date[1:]) != None:
                dates.append(date[1:])
    chunkParser = nltk.RegexpParser(chunkVicVb)
    chunked = chunkParser.parse(chunk)
    chunkVictim = []
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Murder'):
        chunkVictim.append(subtree)
        if chunkVictim != []:
            verb = chunkVictim[0][0][0]
            lemmatizer = WordNetLemmatizer()
            syn_murder = set([w.lemma_names()[0] for w in
                              wn.synsets(lemmatizer.lemmatize('murder', pos="v")) + wn.synsets(
                                  lemmatizer.lemmatize('attack', pos="v"))])
            if lemmatizer.lemmatize(verb, pos="v") in syn_murder:
                victim = ""
                for node in subtree[1:]:
                    victim = victim + " " + node[0]
                victimes.append(victim[1:])
    if victimes == []:
        chunkParser = nltk.RegexpParser(chunkVicNom)
        chunked = chunkParser.parse(chunk)
        chunkVictim = []
        for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Murder'):
            chunkVictim.append(subtree)
            if chunkVictim != []:
                noun = chunkVictim[0][0][0]
                prep = chunkVictim[0][1][0]
                lemmatizer = WordNetLemmatizer()
                syn_murder = set([w.lemma_names()[0] for w in wn.synsets(lemmatizer.lemmatize('murder', pos="n"))])
                if lemmatizer.lemmatize(noun, pos="n") in syn_murder and prep == 'of':
                    victim = ""
                    for node in subtree[2:]:
                        victim = victim + " " + node[0]
                    victimes.append(victim[1:])
    if victimes != [] and victimes != None and dates != [] and dates != None:
        return (victimes[0], dates[0])
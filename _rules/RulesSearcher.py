import nltk
import re

from _planning.CleanProcess import cleanText
import _rules.InfoEnq


#On utilise la tokenisation des mots dans notre phrase pour retourner des tokens
def tokenizePhrase(txt):
    tokens = nltk.sent_tokenize(cleanText(txt))
    return tokens


#On retourne les chunks contenant <IN>*?<NNP>*?<VB.?|NN|NNP|DT>+<IN>*?<...?.?>*?<NNP|CD>+<NN>*?, on utilise la librairie re pour traiter ce genre d'expression
def process_content(text):
    sentences = set(_rules.InfoEnq.getMurderVb(text) + _rules.infoEnq.getMurderNom(text))
    chunks = []
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
                chunks.append(subtree)
    except Exception as exception:
        print(exception)
    return chunks

#On retourne dans un tableau de chunk les chunks qui contiennent <IN><NNP>*?<CD>+<NN|NNP|DT|PRP.?>+<VB.?><...?.?>*?<NN.?.?><IN>*?<...?.?>*?<NNP|CD>+<NN>*
def motifChunk(text):
    sentences = set(_rules.infoEnq.getMurderVb(text) + _rules.infoEnq.getMurderNom(text))
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



#librairie permettant les opérations de bases sur des expressions rationels
import re
#Utilisation de lxml pour manipuler le fichier xml
from lxml import etree
#Gérer des types de données de conteneurs
import collections

#on met l'arbre à 0 pour l'utiliser
def strip_ns_prefix(tree):
    query = "descendant-or-self::*[namespace-uri()!='']"
    for element in tree.xpath(query):
        element.tag = etree.QName(element).localname
    return tree

#On affiche les tags de l'arbre et on nettoie ce qu'on veut pas
def cleanTree(tree,disp,namespace):
    if not namespace:
        tree = strip_ns_prefix(tree)
    nice_tree = collections.OrderedDict()
    for tag in tree.iter():
        path = re.sub('\[[0-9]+\]', '', tree.getpath(tag))
        if path not in nice_tree:
            nice_tree[path] = []
        if len(tag.keys()) > 0:
            nice_tree[path].extend(attrib for attrib in tag.keys() if attrib not in nice_tree[path])
    if disp:
        for path, attribs in nice_tree.items():
            indent = int(path.count('/') - 1)
            print('{0}{1}: {2} [{3}]'.format('    ' * indent, indent, path.split('/')[-1],', '.join(attribs) if len(attribs) > 0 else '-'))


# On récupére le nom en fonction du titre de la page, chaque titre de page= un nom et on fait notre liste de tueur
def fctKillerList():
    wiki_tree = etree.parse('FichiersXml/CorpusXml.xml')
    cleanTree(wiki_tree, False, False)
    killers_list = []
    for user_id in range(len(wiki_tree.xpath("/mediawiki/page"))):
        name = wiki_tree.xpath("/mediawiki/page/title")[user_id].text
        txt = wiki_tree.xpath("/mediawiki/page/revision/text")[user_id].text
        killer = (name, txt)
        killers_list.append(killer)
    return killers_list

killer_list = fctKillerList()

#On retourne la pos min et max du texte à partir de beginning pour pouvoir le parcourir
def getPosMinMax(beginning, txt):
    if beginning not in txt:
        return (0, 0)
    else:
        index_beginning_txt = txt.index(beginning)
        i_min = -1
        i_course = index_beginning_txt - 1
        while i_min == -1:
            if txt[i_course] == '{' and txt[i_course - 1] == '{':
                i_min = i_course - 1
            else:
                i_course -= 1
    total_bracket = 2
    i_max = i_min + 2
    while total_bracket > 0 and i_max < len(txt):
        if txt[i_max] == '{':
            total_bracket += 1
        elif txt[i_max] == '}':
            total_bracket -= 1
        i_max += 1
    return i_min, i_max

#on crée et récupère nos indices de début par exemple avant les notes, ref de début de page on traite la majeur partie des cas possible et sinon on retourne l'indice de fin de page
def getTextiR(txt, iR):
    if '==See also==' in txt[iR:]:
        iE = txt.index('==See also==')
    elif '==Notes==' in txt[iR:]:
        iE = txt.index('==Notes==')
    elif '== Literature ==' in txt[iR:]:
        iE = txt.index('== Literature ==')
    elif '==References==' in txt[iR:]:
        iE = txt.index('==References==')
    elif '==External links==' in txt[iR:]:
        iE = txt.index('==External links==')
    elif '==Citations==' in txt[iR:]:
        iE = txt.index('==Citations==')
    else: iE = -1
    if iE > -1:
        return iR, iE
    else:
        return iR, -1

# on renvoie ce qu'on pense utile à l'enquéteur
def getTextForEnq(txt):
    if '#REDIRECT' in txt:
        return "", ""
    elif 'Infobox serial killer' in txt:
        (containInfoStart, containInfoEnd) = getPosMinMax("Infobox serial killer", txt)
        (txt_begin, txt_end) = getTextiR(txt, containInfoEnd + 1)
    elif 'Infobox murderer' in txt:
        (containInfoStart, containInfoEnd) = getPosMinMax("Infobox murderer", txt)
        (txt_begin, txt_end) = getTextiR(txt, containInfoEnd + 1)
    elif 'Infobox person' in txt or 'Infobox Person' in txt:
        (containInfoStart, containInfoEnd) = getPosMinMax("Infobox person", txt)
        (txt_begin, txt_end) = getTextiR(txt, containInfoEnd + 1)
    elif 'Infobox criminal' in txt:
        (containInfoStart, containInfoEnd) = getPosMinMax("Infobox criminal", txt)
        (txt_begin, txt_end) = getTextiR(txt, containInfoEnd + 1)
    elif 'Infobox officeholder' in txt:
        (containInfoStart, containInfoEnd) = getPosMinMax("Infobox officeholder", txt)
        (txt_begin, txt_end) = getTextiR(txt, containInfoEnd + 1)
    elif 'Infobox' in txt:
        (containInfoStart, containInfoEnd) = getPosMinMax("Infobox", txt)
        (txt_begin, txt_end) = getTextiR(txt, containInfoEnd + 1)
    else:
        (containInfoStart, containInfoEnd) = (0, 0)
        (txt_begin, txt_end) = getTextiR(txt, 0)
    return txt[containInfoStart:containInfoEnd], txt[txt_begin:txt_end]


# Renvoie True si au moins une des liste de la liste est non vide
def is_partly_completed(list):
    for x in list[1:]:
        if x != []:
            return True
    return False

# Nettoie un set d'informations pour éviter les doublons d'tabInfo (date partielle et date complète par exemple)
def cleanDoub(set):
    a_supprimer = []
    for element in set:
        for s in set:
            if element in s and element != s:
                a_supprimer.append(element)
    for x in a_supprimer:
        set.remove(x)
    return set

#On test si la liste parmis l'ensemble des listes est non vide
def isFull(list):
    for x in list:
        if x == []:
            return False
    return True

#dans cette partie on retire tout ce qui va posé problème, ce qui est inutile dans le traitement de notre "enquête"
def cleanText(txt):
    cleanTxt=re.sub(r'ref.*?/ref', '', txt, flags=re.DOTALL)
    cleanTxt=re.sub('&lt;ref name=.*?&gt;', '', txt, flags=re.MULTILINE)
    cleanTxt=re.sub(r'<ref name=.*?>', '', txt, flags=re.MULTILINE)
    cleanTxt= re.sub(r'{{Reflist}}.*', '', txt, flags=re.MULTILINE)
    cleanTxt=re.sub(r'File:.*?.jpg.*?\n', '', txt, flags=re.DOTALL)
    cleanTxt=re.sub(r'<\*.*?\n>*', '', txt, flags=re.DOTALL)
    cleanTxt=re.sub(r'\[\[(?P<name>.*?)\|.*?\]\]', r'\1', txt, flags=re.DOTALL)
    cleanTxt=re.sub(r'{{(?P<name>.*?)}}', r'\1', txt, flags=re.DOTALL)
    cleanTxt=re.sub("\[|\]|<>|<|>|\'+|&nbsp;|&lt;|&gt;|", '', txt, flags=re.MULTILINE)
    cleanTxt=re.sub(r'==*.*?==*', '', txt, flags=re.DOTALL)

    return cleanTxt
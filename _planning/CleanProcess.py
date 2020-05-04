#librairie permettant les opérations de bases sur des expressions rationels
import re
#Utilisation de lxml pour manipulé le fichier xml
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
        (infobox_begin, infobox_end) = getPosMinMax("Infobox serial killer", txt)
        (txt_begin, txt_end) = getTextiR(txt, infobox_end + 1)
    elif 'Infobox murderer' in txt:
        (infobox_begin, infobox_end) = getPosMinMax("Infobox murderer", txt)
        (txt_begin, txt_end) = getTextiR(txt, infobox_end + 1)
    elif 'Infobox person' in txt or 'Infobox Person' in txt:
        (infobox_begin, infobox_end) = getPosMinMax("Infobox person", txt)
        (txt_begin, txt_end) = getTextiR(txt, infobox_end + 1)
    elif 'Infobox criminal' in txt:
        (infobox_begin, infobox_end) = getPosMinMax("Infobox criminal", txt)
        (txt_begin, txt_end) = getTextiR(txt, infobox_end + 1)
    elif 'Infobox officeholder' in txt:
        (infobox_begin, infobox_end) = getPosMinMax("Infobox officeholder", txt)
        (txt_begin, txt_end) = getTextiR(txt, infobox_end + 1)
    elif 'Infobox' in txt:
        (infobox_begin, infobox_end) = getPosMinMax("Infobox", txt)
        (txt_begin, txt_end) = getTextiR(txt, infobox_end + 1)
    else:
        (infobox_begin, infobox_end) = (0, 0)
        (txt_begin, txt_end) = getTextiR(txt, 0)
    return txt[infobox_begin:infobox_end], txt[txt_begin:txt_end]


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
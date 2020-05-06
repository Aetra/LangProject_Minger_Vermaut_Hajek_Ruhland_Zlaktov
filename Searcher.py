from _planning.killerList import getAllInfo, researchForSearcher
from _rules.InfoEnq import getText, getNbVictims, getLieu, getDates, getDateVic
#Resitution des informations pour pouvoir les afficher dans l'ordre victime, date début, date fin, le lieux. Ce qui constitue une liste d'informations sur les tueurs
def postAllInfo():
    infoKiller = getAllInfo()
    all_text = getText(True)
    tabForSearcher = []

    for containInfo in infoKiller:
        tabInfo = researchForSearcher(containInfo[1])
        tabForSearcher.append(tabInfo)
    for i, text in enumerate(all_text):
        victims = getNbVictims(text)
        places = getLieu(text)
        dates= getDates(text)
        tabInfo = getDateVic(text)
        if len(tabForSearcher[i][0]) == 0:
            tabForSearcher[i][0].append(text[0])
        if len(victims) > 0 and victims != None:
            tabForSearcher[i][1].append(victims)
        if len(places) > 0 and places != None:
            tabForSearcher[i][2].append(places)
        if len(dates) > 0 and dates != None:
            tabForSearcher[i][5].append(dates)
        if len(tabInfo) > 0 and tabInfo != None:
            tabForSearcher[i][6].append(tabInfo)

    for killer in tabForSearcher:
        print(killer)
    return tabForSearcher

#On renvoie l'ensemble des informations dans un fichier txt, que l'on crée s'il n'existe pas
resultEnquete=postAllInfo()
with open("resultEnquete.txt", "w", encoding = 'utf-8') as f:
    for r in resultEnquete:
        f.write(str(r) +"\n")


postAllInfo()


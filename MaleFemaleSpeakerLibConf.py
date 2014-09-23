# -*- coding: utf-8 -*-
# <nbformat>2</nbformat>

# <markdowncell>

# # Get Number of Female & Male Speakers on German Library Conferences

# <markdowncell>

# With this notebook, the number of female and male speakers on German Library Conferences is calculated.
# 
# First, a list of popular German names for women and men is harvested (to be able to classify the speakers names).
# Then, the conference speakers' first names for each year are harvested and classified.
# Due to some rare/non-German names, a number of unclassified names has to be classified manually.
# Finally, the summary for each year is printed.
# 
# 1. Get list of popular German names for women and men: from website http://www.beliebte-vornamen.de/
# 1. Get speakers' names for the conferences 2009 - 2014: from website http://www.bib-info.de/verband/publikationen/opus/
# 1. Classify speakers' names
# 1. Calculating the numbers for each year
# 1. Summary

# <codecell>

# 0. 
import bs4
from bs4 import BeautifulSoup
# on use cf. http://www.crummy.com/software/BeautifulSoup/

import urllib2
# on use cf. http://www.pythonforbeginners.com/python-on-the-web/how-to-use-urllib2-in-python/

import json


#retrieve the html-code as Soup
def getHTMLsoup(url):
    HTMLsoup = urllib2.urlopen(url)
    HTMLsoup = BeautifulSoup(HTMLsoup.read()) 
    return HTMLsoup

# <markdowncell>

# ## 1. Get list of popular German names for women and men

# <markdowncell>

# ### Function definitions

# <codecell>

# retrieve the list of female and male names
def nameSoup(url):
    tag_td_women = getHTMLsoup(url).td                        # get column with women's names
    tag_td_men = tag_td_women.find_next_sibling('td')    # get next column (with men's names)
    return tag_td_women, tag_td_men

# make a list of the names from the website "http://www.beliebte-vornamen.de/3774-1970er-jahre.htm/" etc.
def makeList(souplist):
    pureText = souplist.get_text("/", strip=True)  # separate elements with "/" and strip off whitespace
    pureList = pureText.split("/")                 # split into a list
    finalList = []
    for e in pureList:
        e = e.strip()                              # strip off whitespaces
        if len(e) > 1:                             # in case there's an empty element, add only names with more 
            finalList.append(e)                    # than 1 character to new list
    return finalList

#wrap up function
def wrapNameSoup(url):
    #urlSoup = getHTMLsoup(url)
    souplist = nameSoup(url)
    femaleNameList = makeList(souplist[0])
    maleNameList = makeList(souplist[1])
    return femaleNameList, maleNameList

# merging two lists
def removeDuplicates(nameList_0, nameList_1):
    for name in nameList_1:
        if name not in nameList_0:
            nameList_0.append(name)
    nameList_0.sort()                              # sort list alphabetically
    return nameList_0

# <markdowncell>

# ### Function calls

# <codecell>

#start with the 70's
#nameLists[0] = female, nameList[1] = male names
nameLists_70s = wrapNameSoup('http://www.beliebte-vornamen.de/3774-1970er-jahre.htm/')

#get list of the 50's
nameLists_50s = wrapNameSoup('http://www.beliebte-vornamen.de/3770-1950er-jahre.htm')

#get list of the 90's
nameLists_90s = wrapNameSoup('http://www.beliebte-vornamen.de/3778-1990er-jahre.htm')

#get list of the 2000's
nameLists_00s = wrapNameSoup('http://www.beliebte-vornamen.de/3780-2000er-jahre.htm')

#get list of the 20's
nameLists_20s = wrapNameSoup('http://www.beliebte-vornamen.de/3764-1920er-jahre.htm')

# <codecell>

# merge lists and remove duplicates
# 1
femaleNameList = removeDuplicates(nameLists_70s[0], nameLists_50s[0])
maleNameList = removeDuplicates(nameLists_70s[1], nameLists_50s[1])

# 2
femaleNameList = removeDuplicates(femaleNameList, nameLists_90s[0])
maleNameList = removeDuplicates(maleNameList, nameLists_90s[1])

# 3
femaleNameList = removeDuplicates(femaleNameList, nameLists_00s[0])
maleNameList = removeDuplicates(maleNameList, nameLists_00s[1])

# 4
femaleNameList = removeDuplicates(femaleNameList, nameLists_20s[0])
maleNameList = removeDuplicates(maleNameList, nameLists_20s[1])

# <codecell>

# store in lists in a dictionary
dicNames = {'men': maleNameList, 'women': femaleNameList}

#save dictionary as a json-file
with open('germanNames.json', 'wb') as outfile:
    json.dump(dicNames, outfile)

# <markdowncell>

# ## 2. Getting speakers' names

# <codecell>

# functions for retrieving speakers' names from German Library Conferences
# 'http://www.bib-info.de/verband/publikationen/opus/bremen-2014/referenten-a-z.html' etc.

def cleaningList(confSoup):
    #get all <li> tags under the <ul> tag in <div id="inhalt">
    nameSoup = confSoup.find(id='inhalt').find_all('li')
    
    # create list of dictionaries with speakers first names and info, if they had co-speakers
    listOfSpeakers = []
    for e in nameSoup:
        dictOfSpeakers = {}
        try:
            e.a.decompose()
            text = e.get_text(":", strip=True)
            
            #
            #
            if "," not in text:
                dictOfSpeakers['name']= text[text.find(' ')+1:]
            else:
                i1 = text.find(',')+1               # find the first comma (separating second and first name)
                dictOfSpeakers['name'] = text[i1:].strip()
            #
            #
            
            
            if 'Dr.' in dictOfSpeakers['name'][:4]:       # in some cases, ":Dr.: is between second and first name
                i2 = dictOfSpeakers['name'].find(":", 2)  # this if code deletes the :Dr.:
                dictOfSpeakers['name'] = dictOfSpeakers['name'][i2:].strip(":")
            else:
                pass
            if "al." not in text:    # identify co-speakers (who are indicated by et al., et. al., or et.al.)
                dictOfSpeakers['solo'] = 1
            else:
                dictOfSpeakers['solo'] = 0
                #i2=dictOfSpeakers['name'].find(":")             # strip off everything behind first ":"
                #dictOfSpeakers['name'] = dictOfSpeakers['name'][:i2]
            
            i2=dictOfSpeakers['name'].find(":")
            if i2 != -1:
                dictOfSpeakers['name'] = dictOfSpeakers['name'][:i2]
            else:
                dictOfSpeakers['name'] = dictOfSpeakers['name'].rstrip(":") # strip off trailing ":" to keep just first name(s)

            
            listOfSpeakers.append(dictOfSpeakers)
        except AttributeError:        # in case there are invalid <li> tags (there are :o)
            pass
    cleanList = cleaningNames(listOfSpeakers)
    return cleanList

def cleaningNames(LoD):
    for e in LoD:
        #print e['name']
        index1 = e['name'].find(" ")          # keeping only the first of multiple first names (e.g. "Jan Ulrich" > "Jan")
        if index1 != -1:
            e['name'] = e['name'][:index1]
        index2 = e['name'].find("-")          # keeping only the first of multiple first names (e.g. "Jan-Ulrich" > "Jan")
        if index2 != -1:
            e['name'] = e['name'][:index2]
        e['name'] = e['name'].strip(';,')
        #print e['name']
    return LoD

# wrap up function
def getSpeakers(listOfConferenceURLs):
    LoD = []
    for url in listOfConferenceURLs:
        year_index0 = url.rfind('/')
        confDate = int(url[(year_index0 - 4):year_index0])
        
        confSoup = getHTMLsoup(url)
        cleanlist = cleaningList(confSoup)
        
        for speaker in cleanlist:
            speaker['year'] = confDate
            LoD.append(speaker)
            
    return LoD
        # get names for that year
        # write year in dictionary

# <markdowncell>

# ### Function calls

# <codecell>

#pre 2009, the structure of the websites were different 
#(not organized with <li>, just <p>s, or no presenter sorted list))

listOfConferenceURLs = [
'http://www.bib-info.de/verband/publikationen/opus/erfurt-2009/referenten-a-z.html',
'http://www.bib-info.de/verband/publikationen/opus/leipzig-2010/referenten-a-z.html',
'http://www.bib-info.de/verband/publikationen/opus/berlin-2011/referenten-a-z.html',
'http://www.bib-info.de/verband/publikationen/opus/hamburg-2012/referenten-a-z.html',
'http://www.bib-info.de/verband/publikationen/opus/leipzig-2013/referenten-a-z.html', 
'http://www.bib-info.de/verband/publikationen/opus/bremen-2014/referenten-a-z.html']

# <codecell>

# get all the names of the speakers of the conferences 2009 - 2014 (who published their presentations!)
speakerNames = getSpeakers(listOfConferenceURLs)

#save dictionary as a json-file
with open('speakerNames.json', 'wb') as outfile:
    json.dump(speakerNames, outfile)

print
print "In total, " + str(len(speakerNames)) + " speakers' names were recorded."

# <markdowncell>

# ## 3. Classify speakers' names

# <markdowncell>

# ### Function definition

# <codecell>

def classify(dicOfSpeakers, dicOfNames):
    maleSpeaker = 0
    femaleSpeaker = 0
    notInList = 0
    for speaker in dicOfSpeakers:
        if speaker['name'] in dicOfNames['men']:
            maleSpeaker += 1
            speaker['gender'] = 4
        elif speaker['name'] in dicOfNames['women']:
            femaleSpeaker += 1
            speaker['gender'] = 3
        else:
            if len(speaker['name']) > 0 and speaker['name'][-1] == 'a':
                femaleSpeaker += 1
                speaker['gender'] = 3
            elif len(speaker['name']) > 0 and speaker['name'][-2:] == 'us' or speaker['name'][-2:] == 'er' or speaker['name'][-3:] == 'ert':
                femaleSpeaker += 1
                speaker['gender'] = 4
            else:
                notInList += 1
                speaker['gender'] = 5
    print "In total, of the " + str(maleSpeaker + femaleSpeaker + notInList) + " speakers,"
    print (len("In total, of the ") + 1) * " " + str(femaleSpeaker) + " were women,"
    print (len("In total, of the ") + 1) * " " + str(maleSpeaker) + " were men, and"
    print (len("In total, of the ") + 2) * " " + str(notInList) + " names could not be classified."
    return dicOfSpeakers, femaleSpeaker, maleSpeaker

# <markdowncell>

# ### Function call

# <codecell>

with open('speakerNames.json', 'rb') as f:
    dicOfSpeakers = json.load(f)
with open('germanNames.json', 'rb') as f:
    dicOfNames = json.load(f)

# <codecell>

classifiedNames = classify(dicOfSpeakers, dicOfNames)

# <codecell>

import collections
listOfUnclassifiedNames = []
for e in testXY:
    if e['gender'] == 5:
        listOfUnclassifiedNames.append(e['name'])
countedNames=collections.Counter(listOfUnclassifiedNames)
print
print "These names could not be classified as male or female:"
print len("These names could not be classified as male or female:") * "="
print
print countedNames

# <markdowncell>

# ### Now classifying the names manually
# 
# * __male:__ ['Alexandru', 'Andres', 'Anouar', 'Ato', 'Benno', 'Christophe', 'Cornel', 'Curtis', 'Dale', 'Damiel', 'Elmar', 'Enne', 'Fedor', 'Fr\xe9d\xe9ric', 'Gerhardt', 'Hanke', 'Hardy', 'Jarmo', 'Joerg', 'Jorge', 'Kontad', 'Leonhard', 'Najko', 'Nando', 'Nis', 'Oke', 'Pablo', 'Patrice', 'Ross', 'Siegmund']
# * __female:__ ['Aline', 'Almuth', 'Annelen', 'Babett', 'Catherine', 'Dawn', 'Deborah', 'Diane', 'Effi', 'Haike', 'Isolde', 'Karolin', 'Katy', 'Loes', 'Margo', 'Ozlem', 'Rachel', 'Sibel', 'Sigrun', 'Sook', 'Sueje', 'Suenje', 'S\xc3\xbcnje', 'Urs', '[Regine] Dehnel']
# * __undefined:__ "", "u.a."
# 
# ___That is in total for those names:___
# 
# * __male:__ 37
# * __female:__ 27
# * __undefined:__ 5

# <markdowncell>

# ### Summary

# <codecell>

# updating the values manually
femaleSpeaker = classifiedNames[1] + 27
maleSpeaker = classifiedNames[2] + 37
print 
print "In total, of the " + str(maleSpeaker + femaleSpeaker + 5) + " speakers,"
print (len("In total, of the ") + 1) * " " + str(femaleSpeaker) + " were women,"
print (len("In total, of the ") + 1) * " " + str(maleSpeaker) + " were men, and"
print (len("In total, of the ") + 3) * " " + str(5) + " names could not be classified."

# <markdowncell>

# ## 4. Calculating the numbers for each year

# <markdowncell>

# ### Function definition

# <codecell>

def calcPerYear(dicOfSpeakers):
    yearList = [2009, 2010, 2011, 2012, 2013, 2014]
    summaryList = []
    for y in yearList:
        yearDic = {}
        yearDic['year'] = y
        female = 0
        male = 0
        undefList = []
        for e in dicOfSpeakers:
            if e['year'] == y:
                if e['gender'] == 3:
                    female += 1
                elif e['gender'] == 4:
                    male += 1
                else:
                    undefList.append(e['name'])
            
        yearDic['male'] = male
        yearDic['female'] = female
        yearDic['undefNames'] = undefList
        #print yearDic
        summaryList.append(yearDic)
    return summaryList
        

# <markdowncell>

# ### Function call

# <codecell>

dicperYear = calcPerYear(classifiedNames[0])

# <markdowncell>

# ### Updating each year manually

# <codecell>

for e in dicperYear:
    print e
    print

# <codecell>

# 2009
# male 8, female 4
dicperYear[0]['undef'] = 0
dicperYear[0]['male'] = dicperYear[0]['male'] + 8
dicperYear[0]['female'] = dicperYear[0]['female'] + 4

#2010
# male 3, female 5
dicperYear[1]['undef'] = 0
dicperYear[1]['male'] = dicperYear[1]['male'] + 3
dicperYear[1]['female'] = dicperYear[1]['female'] + 5

#2011
# male 4, female 2, undef 4
dicperYear[2]['undef'] = 4
dicperYear[2]['male'] = dicperYear[2]['male'] + 4
dicperYear[2]['female'] = dicperYear[2]['female'] + 2

#2012
# male 6, female 5, undef 1
dicperYear[3]['undef'] = 1
dicperYear[3]['male'] = dicperYear[3]['male'] + 6
dicperYear[3]['female'] = dicperYear[3]['female'] + 5

#2013
# male 6, female 4
dicperYear[4]['undef'] = 0
dicperYear[4]['male'] = dicperYear[4]['male'] + 6
dicperYear[4]['female'] = dicperYear[4]['female'] + 4

#2014
# male 9, female 8
dicperYear[5]['undef'] = 0
dicperYear[5]['male'] = dicperYear[5]['male'] + 9
dicperYear[5]['female'] = dicperYear[5]['female'] + 8

# <codecell>

#save as a json-file
with open('summary.json', 'wb') as outfile:
    json.dump(dicperYear, outfile)

# <markdowncell>

# ## 5. Summary

# <codecell>

newList = []
for e in dicperYear:
    c = e.copy()
    del c['undefNames']
    newList.append(c)
import pprint
pprint.pprint(newList)

# <codecell>



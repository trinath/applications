import linecache
import math
import bisect
import subprocess
import base
import sys
import porter2
import math
import pytrie
import operator
import heapq
import re
import pickle
import time
from collections import OrderedDict
global stop_list
global titlewidth
global sec
h=open("titlesec","r")
titlewidth=h.readline()
titlewidth=base.base62todecimal(titlewidth.strip("\n"))
sec=pickle.load(h)
h.close()

def getMainMemory():
    process=subprocess.Popen("head -1 /proc/meminfo| awk '{print $2}'",shell=True,stdout=subprocess.PIPE)
    M=process.communicate()
    Memory=int(M[0].strip("\n"))
    return Memory

def getStopWords():
    f=open("finalstoplist","r")
    global stop_list
    stop_list=pytrie.StringTrie()
    l=re.split('[\s+]',f.read())
    for i in l:
        stop_list[i]=0
    f.close() 

def gettitle(docid):
    global titlewidth
    global sec
    f=open("titles","r")
    keys=map(lambda x:base.base62todecimal(x),sec.keys())
    index=bisect.bisect_left(keys,docid)
    if keys[index]!=docid:
        index-=1
    #print index,keys[index],base.decimaltobase62(keys[index])
    seek=base.base62todecimal(sec[base.decimaltobase62(keys[index])])
    f.seek(seek)
    counter=0
    while counter<=titlewidth:
        line=f.readline()
        txt=line.split("$",1)
        if txt[0]==base.decimaltobase62(docid):
            return txt[1]
        counter+=1
    f.close()
#query=raw_input('Enter query:')
#inputfile=raw_input('Enter primary index file:')
#outfile=raw_input('Enter secondary index file:')
query1="T : Thierry T : Henry"
query2="T : sachin T : Tendulkar"
query3="I : greek B : python C : mythology"
query4="T : ice B : glacial B : jura B : drumlins"

start=time.time()
query="B : Rajeev B : Sangal"
inputfile="searchindex40gb"
outfile="secondaryindex40gb"
l=OrderedDict()
f=open(outfile,"r")
w=f.readline()
if len(w)>0:
    width=base.base62todecimal(w.rstrip("\n"))
for i in f:
    i=i.split(" ",1)
    l[i[0]]=i[1].strip(" \n")
f.close()

g=open(inputfile,"r")
w=g.readline()
if len(w)>0:
    totaldoc=base.base62todecimal(w.rstrip("\n"))

getStopWords()
m=l.keys()
keywords=re.split("[\s+:]",query)
#print keywords
k=0
scores={}
length={}
while k<len(keywords):
    if len(keywords[k])==0:
        k+=1
        continue
    if keywords[k] in "TICOB":
        field=keywords[k]
        k+=1
        continue
    lower=keywords[k].lower()
    if stop_list.has_key(lower):
        k+=1
        continue
    stem=porter2.stem(lower)
    word=bisect.bisect_left(m,stem)
    if m[word]!=stem:
        word-=1
    #print stem,word,m[word],l[m[word]]
    seek=base.base62todecimal(l[m[word]])
    g.seek(seek)
    counter=0
    check=0
    while counter<width:
        line=g.readline()
        line=line.rstrip("\n")
        text=line.split("#",1)
        if text[0]==stem:
            check=1
            break
        counter+=1
    if check==0:
        k+=1
        continue
    text=text[1].split("#",5)
    #print text
    postings=text[5].split("?",5)
    docs=''
    df=0
    #print postings
    if field=='T':
        if len(text[0])>0:
            df=base.base62todecimal(text[0])
            docs=postings[0]
    elif field=='I':
        if len(text[1])>0:
            df=base.base62todecimal(text[1])
            docs=postings[1]
    elif field=='C':
        if len(text[2])>0:
            df=base.base62todecimal(text[2])
            docs=postings[2]
    elif field=='O':
        if len(text[3])>0:
            df=base.base62todecimal(text[3])
            docs=postings[3]
    else:
        if len(text[4])>0:
            df=base.base62todecimal(text[4])
            docs=postings[4]
    if df==0:
        k+=1
        continue
    prevind=-1
    counter=0
    tf=''
    #print df
    #print docs
    for i in range(len(docs)):
        if counter==20000:
            break
        if docs[i]=="!":
            tf=base.base62todecimal(docs[prevind+1:i])
            prevind=i
        if docs[i]=="$" or docs[i]==":":
            counter+=1
            docid=docs[prevind+1:i]
            prevind=i
            if scores.has_key(docid): 
                scores[docid][0]+=1
                scores[docid][1]+=tf*math.log10(totaldoc*1.0/df)
            else: 
                scores[docid]=[1,tf*math.log10(totaldoc*1.0/df)]
    if counter!=1000 and i-prevind>0:
        docid=docs[prevind+1:i+1]
        if scores.has_key(docid):
            scores[docid][0]+=1
            scores[docid][1]+=tf*math.log10(totaldoc*1.0/df)
        else: 
            scores[docid]=[1,tf*math.log10(totaldoc*1.0/df)]
    k+=1
h=[(value[0],value[1],key) for key,value in scores.iteritems()]
heapq.heapify(h)
top=heapq.nlargest(15,h,operator.itemgetter(0,1))
for i in top:
    docid=base.base62todecimal(i[2])
    #print "Doc id(%s): %d"%(i[2],docid)
    print docid,
    #print i
    title=gettitle(docid)
    if title is not None and title.__len__():
        #print "Title: %s"%(title)
        print title,
print ""
print "Time:%f ms"%((time.time()-start)*1000)

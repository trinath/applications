#!/usr/bin/python
import os
import sys
import re
import multiprocessing
import StringIO
import porter2
import pytrie
import time
import heapq
import base
import operator
import subprocess
global path_to_index
global Memory
def getMainMemory():
    global Memory
    process=subprocess.Popen("head -1 /proc/meminfo| awk '{print $2}'",shell=True,stdout=subprocess.PIPE)
    M=process.communicate()
    M=M[0].strip("\n")
    Memory = int(M)
    print Memory


def getStopWords():
    f=open("finalstoplist","r")
    global stop_list
    stop_list={}
    l=re.split('[\s+]',f.read())
    for i in l:
        stop_list[i]=0
    f.close() 


def printTrie(filecounter,pagetrie):
    s="subtemp%d"%(filecounter)
    print "Print to file",s
    f=open(s,"w")
    text=[]
    sort=sorted(pagetrie.iteritems(),key=operator.itemgetter(0))
    for key,value in sort:
        #print key,value
        flags=[]
        for i in value[5:]:
            temp=sorted(i.iteritems(),key=operator.itemgetter(1),reverse=True)
            flag=[]
            flag1=[]
            c=0
            for j in temp:
                if j[1]!=c: 
                    c=j[1]
                    if flag: 
                        flag1.append(":".join(flag))
                        flag=[]
                    flag.append("%s!%s"%(base.decimaltobase62(j[1]),j[0]))
                else:
                    flag.append(j[0])
            if flag:
                flag1.append(":".join(flag))
            flags.append("$".join(flag1))
        postlist="?".join(flags)
        text.append("#".join([key,"#".join(map(lambda x: str(x) if x>0 else '',value[:5])),postlist])+"\n")
    f.writelines(text)
    f.close()

def processWikiText(ipfile,file):
    f=open(ipfile,"r")
    pagetrie=dict()
    lines=f.readlines()
    f.close()
    lenlines=lines.__len__()
    i=0
    count=0
    title=''
    docId=''
    text=''
    infoflag=0
    catflag=0
    txtflag=0
    outflag=0
    tflag=0
    start=time.time()
    while i<lenlines:
        line=lines[i].lstrip(" ")
        line=line.rstrip("\n")
        if line=="<page>":
            i+=1
            line=lines[i].lstrip(" ")
            line=line.rstrip("\n")
            if line[:7]=="<title>":
                title=line[7:-8]
            i+=2
            line=lines[i].lstrip(" ")
            line=line.rstrip("\n")
            if line[:4]=="<id>":
                docId=line[4:-5]
                docId=base.decimaltobase62(int(docId))
            term=''
            tlength=title.__len__()
            for j in xrange(tlength):
                lower=title[j].lower()
                if lower<'a' or lower>'z':
                    if term:
                        if not(stop_list.has_key(term)):
                            stem=porter2.stem(term)
                            if pagetrie.has_key(stem):
                                v=pagetrie[stem]
                                if v[5].has_key(docId):
                                    v[5][docId]+=1
                                else:
                                    v[0]+=1
                                    v[5][docId]=1
                            else:
                                pagetrie[stem]=[1,0,0,0,0,{docId:1},{},{},{},{}]
                    term=''
                else:
                    term+=lower
            if len(term)>0 and not(stop_list.has_key(term)):
                stem=porter2.stem(term)
                if pagetrie.has_key(stem):
                    v=pagetrie[stem]
                    if v[5].has_key(docId):
                        v[5][docId]+=1
                    else:
                        v[0]+=1
                        v[5][docId]=1
                else:
                    pagetrie[stem]=[1,0,0,0,0,{docId:1},{},{},{},{}]
            infoflag=0
            catflag=0
            txtflag=1
            outflag=0
            print docId,title
            i+=1
            continue
        elif line[:7]=="</page>":
            count+=1
            i+=1
            continue
        elif line[:5]=="<text":  #text flag
            l=line.split(">",1)
            text=[]
            if l[1][-7:]=="</text>":
                line=l[1].rsplit("<",1)
                text.append(l[0])
                i+=1
            else:
                text.append(l[1])
                i+=1
                while True:
                    if lines[i][-8:]=="</text>\n":
                        line=lines[i].rsplit("<",1)
                        text.append(line[0])
                        break
                    text.append(lines[i])
                    i+=1
            text="".join(text)
            text="%s\n"%(text)
            txtlength=text.__len__()
            j=0
            term=''
            txtflag=1
            prevind=0
            flag=0
            while j<txtlength:
                if text.startswith("[[",j):
                    j+=2
                    if (text.startswith("Cate",j)):
                        catflag=1
                        flag=1
                        j+=9
                    else:
                        if flag==1: break
                        outflag=1
                    term=''
                    txtflag=0
                    while 1:
                        check=0
                        if text.startswith("]",j):
                            check=1
                        lower=text[j].lower()
                        if lower<'a' or lower>'z':
                            if len(term)>2:
                                if not(stop_list.has_key(term)):
                                    stem=porter2.stem(term)
                                    if pagetrie.has_key(stem):
                                        v=pagetrie[stem]
                                        if infoflag: 
                                            if v[6].has_key(docId):
                                                v[6][docId]+=1
                                            else:
                                                v[1]+=1
                                                v[6][docId]=1
                                        if catflag: 
                                            if v[7].has_key(docId):
                                                v[7][docId]+=1
                                            else:
                                                v[2]+=1 
                                                v[7][docId]=1
                                        if outflag: 
                                            if v[8].has_key(docId):
                                                v[8][docId]+=1
                                            else:
                                                v[3]+=1 
                                                v[8][docId]=1
                                    else:
                                        pagetrie[stem]=[0,infoflag,catflag,outflag,0,{},{},{},{},{}]
                                        v=pagetrie[stem]
                                        if infoflag: v[6][docId]=1
                                        if catflag: v[7][docId]=1
                                        if outflag: v[8][docId]=1
                            term=''
                        else:
                            term+=lower
                        if check==1:
                            outflag=0
                            catflag=0
                            j+=2
                            break
                        j+=1
                    if not(infoflag): txtflag=1
                elif text.startswith("{{",j):
                    j+=2
                    if text.startswith("Info",j):
                        infoflag=1
                        txtflag=0
                        j+=7
                        #print "infostart",infoflag
                    else:
                        while 1:
                            if text[j]=="}" or text[j]=='\n':
                                j+=2
                                break
                            j+=1
                elif text.startswith("}}\n",j):
                    infoflag=0
                    txtflag=1
                    #print "infoclose",infoflag
                    j+=3
                else:
                    lower=text[j].lower()
                    if lower<'a' or lower>'z':
                        if j-prevind>3: #j-prevind-1 == length
                            term=text[prevind+1:j].lower()
                            if not(stop_list.has_key(term)):
                                stem=porter2.stem(term)
                                if pagetrie.has_key(stem):
                                    v=pagetrie[stem]
                                    if infoflag: 
                                        if v[6].has_key(docId):
                                            v[6][docId]+=1
                                        else:
                                            v[1]+=1 
                                            v[6][docId]=1
                                    if catflag: 
                                        if v[7].has_key(docId):
                                            v[7][docId]+=1
                                        else:
                                            v[2]+=1 
                                            v[stem][7][docId]=1
                                    if outflag: 
                                        if v[8].has_key(docId):
                                            v[8][docId]+=1
                                        else:
                                            v[3]+=1 
                                            v[8][docId]=1
                                    if txtflag: 
                                        if v[9].has_key(docId):
                                            v[9][docId]+=1
                                        else:
                                            v[4]+=1 
                                            v[9][docId]=1
                                else:
                                    pagetrie[stem]=[0,infoflag,catflag,outflag,txtflag,{},{},{},{},{}]
                                    v=pagetrie[stem]
                                    if infoflag: v[6][docId]=1
                                    if catflag: v[7][docId]=1
                                    if outflag: v[8][docId]=1
                                    if txtflag: v[9][docId]=1
                        prevind=j
                    j+=1
                    continue
                prevind=j
        i+=1
    print "proc%d"%(file)
    printTrie(file,pagetrie)
    pagetrie.clear()
    return count

def removeFiles(n):
    curdir=os.getcwd()
    for i in range(1,n+1,1):
        curpath=curdir+'/temp%d'%(i)
        if os.path.exists(curpath):
            os.unlink(curpath)

def shortmerge(c,d):
    clength=c.__len__()
    dlength=d.__len__()
    if clength==0 and dlength==0:
        return ''
    if c=='': 
        c=[]
    else:
        c=c.split("$")
    if d=='': 
        d=[]
    else:
        d=d.split("$")
    l=[]
    i=0
    j=0
    clength=c.__len__()
    dlength=d.__len__()
    def m(x):
        t=x.split("!",1)
        return (base.base62todecimal(t[0]),t[1])
    a=map(m,c)
    b=map(m,d)
    while (i<clength or j<dlength):
        if i==clength and j==dlength:
            break
        elif i==clength:
            l.extend(d[j:])
            j+=dlength
        elif j==dlength:
            l.extend(c[i:])
            i+=clength
        else:
            if a[i][0]>b[j][0]:
                l.append(c[i])
                i+=1
            elif a[i][0]<b[j][0]:
                l.append(d[j])
                j+=1
            else:
                l.append("%s!%s:%s"%(base.decimaltobase62(a[i][0]),a[i][1],b[j][1]))
                i+=1
                j+=1
    return "$".join(l)

def merge(a,b):
   a=a.split("?",4)
   b=b.split("?",4)
   final="%s?%s?%s?%s?%s"%(shortmerge(a[0],b[0]),shortmerge(a[1],b[1]),shortmerge(a[2],b[2]),shortmerge(a[3],b[3]),shortmerge(a[4],b[4]))
   return final

def mergeIndex(index_file,n,totaldoc):
    print "Merging Indexes"
    freqthreshold=0.8*totaldoc
    iters=[]
    seeks=[]
    terms=[]
    index=open(index_file,"w")
    if n!=4:
        index.write(base.decimaltobase62(totaldoc)+"\n")
    index.close()
    bufsize=Memory/(2*(n+1))
    l=[]
    for i in range(0,n,1):
        name="temp%d"%(i+1)
        if n==4: name="sub"+name
        #print name,i+1
        f=open(name,"r")
        l.append(f.readlines(bufsize))
        #print i,len(l[i])
        #if len(l[i])==0:
        #    print i+1
        if len(l[i]):
            x=l[i][0].strip("\n").split('#',6)
            x=map(lambda p: '0' if p=='' else p,x)
            seeks.append(f.tell())
            iters.append(1)
            x.append(i)
            heapq.heappush(terms,x)
        else:
            iters.append(0)
            seeks.append(f.tell())
        f.close()
    #print terms,len(l[0])
    termtrie=pytrie.SortedStringTrie()
    print terms
    text=[]
    count=n
    while len(terms)>0:
        t=heapq.heappop(terms)
        #print t
        if termtrie.has_key(t[0]):
            value=termtrie[t[0]]
            items=[int(t[i+1])+value[i] for i in xrange(5)]
            if sum(items)<freqthreshold:
                items.append(merge(t[6],value[5]))
            else:
                items.append("")
            termtrie[t[0]]=items
        else:
			items=map(lambda x:int(x),t[1:-2])
			items.append(t[6])
			termtrie[t[0]]=items

        if len(termtrie)>n:
            text.append("\n".join([ "#".join([key,"#".join(map(lambda x: base.decimaltobase62(x) if x>0 else '',value[:-1])),value[5]]) for key,value in termtrie.iteritems() if value[5]!=''])+"\n")
            termtrie.clear()
    
        if text.__sizeof__()>bufsize:
            print "Index transfer to file"
            index=open(index_file,"a")
            index.writelines(text)
            index.close()
            text=[]
        
        if iters[t[7]]<len(l[t[7]]):
            line=l[t[7]][iters[t[7]]]
            iters[t[7]]+=1
        else:
            line=''
            m=t[7]
            name="temp%d"%(m+1)
            if n==4: name="sub"+name
            f=open(name,"r")
            f.seek(seeks[m])
            if count==1:
                if len(termtrie)>0: text.append("\n".join([ "#".join([key,"#".join(map(lambda x: base.decimaltobase62(x) if x>0 else '',value[:-1])),value[5]]) for key,value in termtrie.iteritems() if value[5]!=''])+"\n")
                termtrie.clear()
                index=open(index_file,"a")
                index.writelines(text)
                text=[]
                while 1:
                    line=f.read(bufsize)
                    if len(line)==0: break
                    index.write(line)
                break
                index.close()
            l[m]=f.readlines(bufsize)
            if len(l[m]):
                line=l[m][0]
                iters[m]=1
                seeks[m]=f.tell()
            else:
                count-=1
            f.close()
        if len(line)>0:
            x=line.strip("\n").split('#',6)
            x=map(lambda p: '0' if p=='' else p,x)
            x.append(t[7])
            heapq.heappush(terms,x)

    if len(termtrie)>0 or len(text)>0:
        index=open(index_file,"a")
        text.append("\n".join([ "#".join([key,"#".join(map(lambda x: base.decimaltobase62(x) if x>0 else '',value[:-1])),value[5]]) for key,value in termtrie.iteritems() if value[5]!=''])+"\n")
        termtrie.clear()
        index.writelines(text)
        index.close()

    terms=[]
    index.close()
    termtrie.clear()
    print "Removing temp files"
    #Removing temp files created
    #removeFiles(n)


def Addresponse(a,b):
	responses.append(processWikiText(a,b))

if __name__=="__main__":
    global path_to_index
    totaldoc=0
    path_to_split_dir=sys.argv[1]
    path_to_split_dir=path_to_split_dir.strip(" /")
    path_to_split_dir=path_to_split_dir+"/"
    path_to_index=sys.argv[2]
    dir_list=os.listdir(path_to_split_dir)
    getStopWords()
    getMainMemory()
    start=time.time()
    dir_list.sort()
    filecount=len(dir_list)
    print dir_list
    print "Files to be indexed %d" %(filecount)
    totaldoc=[]
    doccount=0
    for i in range(1):
        path_to_file=path_to_split_dir+dir_list[i]
       	print "Indexing file: %s"%(dir_list[i])
        curdir=os.getcwd()
        if os.path.isdir("check"):
            os.system("rm -rf check")
        os.mkdir("check")
        os.chdir("check")
        os.system("split -b 25M --suffix-length=1 ../"+path_to_file)
        sub_dir_list=os.listdir(curdir+"/check")
        sub_dir_list.sort()
        os.chdir(curdir)
        os.system("python quantizing.py check/")
        print sub_dir_list
        manager=multiprocessing.Manager()
        responses=manager.list()
        p=[]
        for j in range(4):
            print "Indexing sub part: %s"%(sub_dir_list[j])
            proc=multiprocessing.Process(target=Addresponse,args=(["check/"+sub_dir_list[j],j+1]))
            p.append(proc)
        for proc in p:
            proc.start()
            proc.join()
        print "Responses:",responses
        doccount=sum(responses)
        print "Files Indexed:%d Pages processed:%d" %(i+1,doccount)
        start1=time.time()
        index_file="temp%d"%(i+1)
        mergeIndex(index_file,4,doccount)
        totaldoc.append(doccount)
        print "Time taken for file %s is"%(dir_list[i]),time.time()-start,time.time()-start1
        start=time.time()
    stop_list.clear()
    start=time.time()
    mergeIndex(path_to_index,filecount,sum(totaldoc))
    print "Time taken for merging",time.time()-start

import math
import subprocess
import base
import sys
import math
import pickle
from collections import OrderedDict
global Memory
process=subprocess.Popen("head -1 /proc/meminfo| awk '{print $2}'",shell=True,stdout=subprocess.PIPE)
M=process.communicate()
Memory=int(M[0].strip("\n"))
bufsize=Memory/3
inputfile=raw_input('Enter title index file:')
outfile=raw_input('Enter title secondary index file:')
g=open(inputfile,"r")
h=open(outfile,"w")
index=OrderedDict()
with open(inputfile,"r") as f:
    count=0
    for i in f:
        count+=1
    width=int(math.sqrt(count))
    #print count,width
    h.write(base.decimaltobase62(width)+"\n")
    counter=0
    f.seek(0)
    offset=0
    l=g.readline()
    if l:
        index[l.split("$")[0]]=base.decimaltobase62(offset)
    for i in f:
        #print i
        offset+=len(i)
        counter+=1
        if counter==width:
            g.seek(offset)
            x=g.readline()
            index[x.split("$")[0]]=base.decimaltobase62(offset)
            #index.append(" ".join([x.split("$")[0],base.decimaltobase62(offset),"\n"]))
            counter=0
        #if sys.getsizeof(index)>bufsize:
        #    h.writelines(index)
        #    index=[]
    if len(index):
        pickle.dump(index,h)
        #h.writelines(index)
        index=[]
g.close()
h.close()

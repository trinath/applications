import math
import subprocess
import base
import sys
import math
global Memory
process=subprocess.Popen("head -1 /proc/meminfo| awk '{print $2}'",shell=True,stdout=subprocess.PIPE)
M=process.communicate()
Memory=int(M[0].strip("\n"))
bufsize=Memory/3
inputfile=raw_input('Enter primary index file:')
outfile=raw_input('Enter secondary index file:')
g=open(inputfile,"r")
h=open(outfile,"w")
index=[]
with open(inputfile,"r") as f:
    doccount=f.readline()
    count=0
    for i in f:
        count+=1
    width=int(math.sqrt(count))
    #print count,width
    h.write(base.decimaltobase62(width)+"\n")
    counter=0
    f.seek(0)
    offset=0
    f.readline()
    offset=len(g.readline())
    l=g.readline()
    if l:
        index.append(" ".join([l.split("#")[0],base.decimaltobase62(offset),"\n"]))
    check=0
    for i in f:
        #print i
        offset+=len(i)
        if check==0:
            check=1
            continue
        counter+=1
        if counter==width:
            g.seek(offset)
            x=g.readline()
            index.append(" ".join([x.split("#")[0],base.decimaltobase62(offset),"\n"]))
            #print i,x,index[-1]
            counter=0
        if sys.getsizeof(index)>bufsize:
            h.writelines(index)
            index=[]
    if len(index):
        h.writelines(index)
        index=[]
g.close()
h.close()

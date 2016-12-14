import sys
import subprocess
import os
import base
import sys
process=subprocess.Popen("head -1 /proc/meminfo| awk '{print $2}'",shell=True,stdout=subprocess.PIPE)
M=process.communicate()
print M[0].strip("\n")
Memory = int(M[0])
if len(sys.argv)<3:
    print "Give split files path and titles file name"
    sys.exit()
path_to_split_dir=sys.argv[1]
path_to_split_dir=path_to_split_dir.strip(" /")
path_to_split_dir=path_to_split_dir+"/"
path_to_title=sys.argv[2]
dir_list=os.listdir(path_to_split_dir)
dir_list.sort()
filecount=len(dir_list)
f=open(path_to_title,"w")
f.close()
for j in range(filecount):
    path_to_file=path_to_split_dir+dir_list[j]
    f=open(path_to_file,"r")
    lines=f.readlines()
    f.close()
    lenlines=len(lines)
    text=[]
    i=0
    while i<lenlines:
        line=lines[i].lstrip(" ")
        if line.startswith("<page>"):
            line=lines[i+1].lstrip(" ")
            line=line.rstrip("\n")
            if line.startswith("<title>",0):
                title=line[7:-8]
            line=lines[i+3].lstrip(" ")
            line=line.rstrip("\n")
            if line.startswith("<id>",0):
                docId=base.decimaltobase62(int(line[4:-5]))
                text.append("$".join([docId,title])+"\n")
                #print docId,title
            i+=3
        i+=1
    if sys.getsizeof(text)>Memory:
        f=open(path_to_title,"a")
        #f.write("\n".join(text))
        f.writelines(text)
        text=[]
        f.close()
    print "File process:%s Titles processed:%d" %(dir_list[j],i+1)
    if len(text)>0:
        f=open(path_to_title,"a")
        f.writelines(text)
        #f.write("\n".join(text))
        text=[]
        f.close()
    


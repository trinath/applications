file=raw_input("")
f=open(file,"r")
totaltime=0
for i in f:
    if i.startswith("Time taken for file"):
        i=i.rsplit(" ",2)
        parsetime=float(i[1])+float(i[2].strip("\n"))
        totaltime+=parsetime
f.close()
print "%f minutes"%(totaltime/60)



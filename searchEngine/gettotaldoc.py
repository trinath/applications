file=raw_input("")
f=open(file,"r")
totaldoc=0
for i in f:
    if i.startswith("Files Indexed"):
        doccount=i.rsplit(":",1)[1].strip("\n")
        totaldoc+=int(doccount)
f.close()
print totaldoc



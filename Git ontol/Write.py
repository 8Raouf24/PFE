
f = open("NewOwl.py","a")
g = open("cat.txt","r")

corpus=g.readlines()

for i in corpus:
    f.write("class "+i[0:-1].replace(' ','_')+"(Thing):\n        pass\n")
from owlready2 import *
import gzip
import json


def parse(path):
    data = []
    with gzip.open(path) as f:
        for l in f:
            data.append(json.loads(l.strip()))
    return data


def ordonner_classe(ontol):
    #On utilise cette fonction pour pouvoir receuillir les classes de notre ontologie dans une liste afin de pouvoir les manipuler
    d = {}
    for i in ontol.classes():
        d[i.name] = i
    d = sorted(d.items(), key=lambda x: x[0])

    L = []
    for i in range(len(d)):
        L.append(d[i][1])
    return L


#def enrichissement(ontol,gen,feature,uri,var,limite=5000):
#    with ontol:
#        M_Category = L[var]
#        liste = []
#        for i in range(limite):
#            article = next(gen)
#            if feature in article.keys():
#                nom = article[feature][1:-1].replace(" ", "")
#
#                Cat = None
#                if nom not in liste:
#                    liste.append(nom)
#                    Cat = M_Category()
#                    Cat.name = nom
#
#                else:
#                    Cat = ontol.search(iri=uri + nom)[0]
#
#                produit = ontol.search(iri="*" + article['asin'])[0]
#                produit.appartient_category = [Cat]
#                Cat.contient_article = [produit]
#                print("fait")

#F://Raouf//Pfe//Coding//Script//Ontologie//sortieVG.owl
onto = get_ontology("Amazon.owl")

data = parse("F:\Raouf\Pfe\Coding\Datasets\Cell phone\meta_Cell_Phones_and_Accessories.json.gz")
my_iri = "http://www.semanticweb.org/msigp/ontologies/2020/3/Amazon_Ontol#"

categories = []
f = open("cat.txt", "w")

for i in range(len(data)):
    print(i)
    #D'abord je vérifie si mon objet json ( mon item ) contient l'information catégorie
    if 'category' in data[i]:
        #Si oui , je vérifie si il contient une chaine vide , car en examinant les données j'ai remarqué que desfois dans la case 'category ' il y'avait une 'description ' , et cette description était souvent précedé par cette chaine vide 
        if '' in data[i]['category']:
            #Donc je ne prends que les sous catégories avant la chaine vide 
            limite = data[i]['category'].index('')
            j = 0
            print(data[i]['category'][0:limite])
            for j in range(limite):
                if data[i]['category'][j] not in categories:
                    categories.append(data[i]['category'][j])
                    f.write(data[i]['category'][j] + "\n")
                j = +1


        else:
            print(data[i]['category'])
            for y in data[i]['category']:
                if y not in categories:
                    categories.append(y)
                    f.write(y + "\n")

    else:
        pass
    i = +1

print(len(categories))
print(categories)

# enrichissement(ontol,data,'brand',my_iri,1)


onto.save("out.owl", format="ntriples")

#enrichissement(ontol,data,'brand',my_iri,1)





onto.save("out.owl", format="ntriples")

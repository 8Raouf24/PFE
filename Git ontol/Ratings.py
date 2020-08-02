from owlready2 import *
import gzip
import json


def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        d = json.loads(l)

        yield d


def ordonner_classe(ontol):
    d = {}
    for i in ontol.classes():
        d[i.name] = i
    d = sorted(d.items(), key=lambda x: x[0])

    L = []
    for i in range(len(d)):
        L.append(d[i][1])
    return L



ontol = get_ontology("F://Raouf//Pfe//Coding//Script//Ontologie//sortieVG.owl").load()
my_classes = ordonner_classe(ontol)
print(my_classes)

data = parse("F:\Raouf\Pfe\Coding\dataset\Meta Data\Video_Games.json.gz")
my_iri = "http://www.semanticweb.org/msigp/ontologies/2020/3/Amazon_Ontol#"
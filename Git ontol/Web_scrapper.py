import gzip
import random
import time
import json
from threading import Thread, RLock

import rdflib
import requests
from lxml import html


class interfaceOntology:
    rdf_ns = "file:///Ontologie/"
    amazone_ns = "http://www.semanticweb.org/msigp/ontologies/2020/3/Amazon_Ontol#"


    # Le constructeur de notre ontologie
    def __init__(self, path, sortie_rdf, sortie_owl, mode,limite=10000):
        self.path = path
        self.sortie_rdf = sortie_rdf
        self.sortie_owl = sortie_owl
        self.mode = mode
        self.verrou_ontologie = RLock()
        self.graph_rdf = rdflib.Graph()
        self.graph_owl = rdflib.Graph()
        self.limite = limite
    # Fonction  pour parse notre ontologie
    def parsing(self):
        self.graph_owl.parse("Amazon_Ontology.owl", format="turtle")
        self.graph_rdf.parse(self.sortie_rdf, format="turtle")

    # Fonction a utilisation unique pour ouvrir en écriture les fichiers
    def initialiser(self):
        open(self.sortie_owl, "w")
        open(self.sortie_rdf, "w")
        open("sortieVG.owl","w")

    # Création d'un article dans notre ontologie
    def create_article(self, asin):
        article_r = rdflib.URIRef(self.rdf_ns + self.path.split(".")[0].split("\\")[-1].split("/")[-1] + "/" + asin)
        article_t = rdflib.URIRef(self.amazone_ns + "Article")
        self.graph_rdf.add((article_r, rdflib.RDF.term("type"), article_t))

    # Création d'un user dans notre ontologie
    def create_reviewer(self, reviewerID):
        reviewer_r = rdflib.URIRef(
            self.rdf_ns + self.path.split(".")[0].split("\\")[-1].split("/")[-1] + "/" + reviewerID)
        reviewer_t = rdflib.URIRef(self.amazone_ns + "Reviewer")
        self.graph_rdf.add((reviewer_r, rdflib.RDF.term("type"), reviewer_t))

    # Modifier les attributs d'un article
    def setAttributes(self, ID, dictionnaire):
        article_r = rdflib.URIRef(self.rdf_ns + self.path.split(".")[0].split("\\")[-1].split("/")[-1] + "/" + ID)
        R = [s.split("#")[-1] for s, p, o in
             self.graph_owl.triples((None, rdflib.RDF.term("type"), rdflib.OWL.term("DatatypeProperty")))]
        for key, val in dictionnaire.items():
            if (not key in R):
                attribute_r = rdflib.URIRef(self.amazone_ns + key)
                self.graph_owl.add((attribute_r, rdflib.RDF.term("type"), rdflib.OWL.term("DatatypeProperty")))
            attribute_r = rdflib.URIRef(self.amazone_ns + key)
            self.graph_rdf.add((article_r, attribute_r, rdflib.Literal(val)))

    def setPrice(self, asin, price):
        article_r = rdflib.URIRef(self.rdf_ns + self.path.split(".")[0].split("\\")[-1].split("/")[-1] + "/" + asin)
        prix_r = rdflib.URIRef(self.amazone_ns + "Prix")
        print("Writing price = ", price, "for asin = ", asin)
        self.graph_rdf.remove((article_r, prix_r, None))
        self.graph_rdf.add((article_r, prix_r, rdflib.Literal(price)))
        self.graph_rdf.serialize(self.sortie_rdf, format="turtle")

    def vider(self):
        self.remplire_from_path()
        self.graph_rdf.serialize(self.sortie_rdf, format="turtle")
        self.graph_owl.serialize(self.sortie_owl, format="turtle")

    def init_ontologie(self):
        L = [(s, p, o) for s, p, o in self.graph_rdf.triples((None, None, None))]
        if len(L) == 0:
            self.remplire_from_path()

    def firstUnkownPrice(self):
        while True:
            request = """
        prefix : <http://www.semanticweb.org/msigp/ontologies/2020/3/Amazon_Ontol#>
        prefix owl: <http://www.w3.org/2002/07/owl#> 
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        SELECT DISTINCT ?article
        WHERE {
        ?article rdf:type :Article . 
        ?article :Prix "UNKNOWN_PRICE"
        }
        """
            r = self.graph_rdf.query(request)
            L = []
            for i in r:
                L.append(str(i[0]).split("/")[-1])
            self.graph_rdf.serialize('test.rdf', format='turtle')

            if (len(L) > 0):
                yield random.choice(L)
            else:
                yield None

    def remplire_from_path(self, limite= 10000):
        if (self.mode == "article"):
            path = self.path
            L = parse(path)
            for i in range(0, limite):
                article = next(L)
                # print(article)
                attributs = dict(
                    Prix=article.get("price", "UNKNOWN_PRICE")
                )
                if ("titre" in article.keys()):
                    attributs.update(Title=article['titre'])
                if ("rank" in article.keys()):
                    attributs.update(SalesRank=article['rank'])
                if ("description" in article.keys()):
                    attributs.update(Description=article.get("description")[0])

                self.create_article(article["asin"])
                self.setAttributes(article["asin"], attributs)
        else:
            path = self.path
            L = parse(path)
            for i in range(0, limite):
                reviewer = next(L)
                attributs = dict(
                    Name=reviewer.get("reviewerName", "UNKNOW_NAME")
                )
                self.create_reviewer(reviewer["reviewerID"])
                self.setAttributes(reviewer["reviewerID"], attributs)


def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        d = json.loads(l)

        yield d


class Seeker(Thread):
    def __init__(self, protected_interface_ontologie, limite, ID=0, attempts=5):
        Thread.__init__(self)
        self.attempts = attempts
        self.limite = limite
        self.interface_ontologie, self.verrou = protected_interface_ontologie, protected_interface_ontologie.verrou_ontologie
        self.ID = ID

    def run(self):
        cpt = 1
        with self.verrou:
            asin = next(self.interface_ontologie.firstUnkownPrice())
        lien = "https://www.amazon.com/dp/" + asin
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0 '}
        r = requests.get(lien, headers=header)
        tree = html.fromstring(r.content)
        c = tree.xpath('//span[contains(@class,"a-color-price")]/text()')
        val = "UNKNOWN_PRICE"
        while (asin != None and cpt < self.limite):
            val = "UNKNOWN_PRICE"
            cpt = cpt + 1

            # Normalement on fait self.interface_ontologie.firstUnknownPrice() c'est pour test
            if (cpt % self.attempts == 0 or val != "UNKNOWN_PRICE"):
                with self.verrou:
                    asin = next(self.interface_ontologie.firstUnkownPrice())
                    lien = "https://www.amazon.com/dp/" + asin
                    print(lien)
            # print(self.ID ," > Seeking for : ", asin)
            r = requests.get(lien, headers=header)
            tree = html.fromstring(r.content)
            c = tree.xpath('//span[contains(@class,"a-color-price")]/text()')
            for i in c:
                if "$" in i:
                    print(' get : ', i.strip())
                    val = i.strip()
                    break
                else:
                    val = "UNKONWN_PRICE"
                    break
                # Normalement
                # self.interface_ontologie.setPrice(val)
            if val == "UNKNOWN_PRICE":
                print(".", end="")
            else:
                with self.verrou:
                    print(self.ID, " >Price found for asin = ", asin, " : ", val)
                    self.interface_ontologie.setPrice(asin, val)
            print(cpt, ",", asin)

data_len = len(list(parse("F:\Raouf\Pfe\Coding\dataset\kcore_5.json.gz")))
ontologie = interfaceOntology("F:\Raouf\Pfe\Coding\dataset\kcore_5.json.gz", "dataVG.rdf","knowledgeVG.owl", "rating")
ontologie.init_ontologie()

ontologie.parsing()

#liste_thread = []
#for i in range(0, 100):
#   time.sleep(0.5)
#   S = Seeker(ontologie, 25, i)
#   S.start()
#   liste_thread.append(S)
#for thread in liste_thread:
#   thread.join()


ontologie.graph_rdf.serialize(ontologie.sortie_rdf, format="turtle")
ontologie.graph_owl.serialize(ontologie.sortie_owl, format="turtle")

ontologie.graph_rdf.serialize("sortieVG_rdf.owl")
ontologie.graph_owl.serialize("sortieVG_owl.owl")

(ontologie.graph_rdf + ontologie.graph_owl).serialize("sortieVG.owl")

print("fin du programme ")
import sys
import os
import argparse
import rdflib
import pyaml
from rdflib.graph import Graph
import pprint
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('file')
args = parser.parse_args()
#On regarde si le fichier existe
if os.path.exists(args.file)  :
	print("Files exist")
	print(args)
#On regarde si le fichier est un .rdf
	if Path(args.file).suffix == '.rdf' :
		with open(args.file) as file:
			g = Graph()
			g.parse(file)
		for s, p, o in g.triples((rdflib.term.URIRef('http://www.iro.umontreal.ca/~lapalme/sujet3'), 
rdflib.term.URIRef('http://www.iro.umontreal.ca/~lapalme/predicat'), None)) :
			pprint.pprint(o)
			
def testMetrique() :
    liste_S = []
    liste_O = []
    points = 0
    nbPossible = 0
    for s, p, o in g.triples((None, 'http://www.w3.org/2000/01/rdf-schema#subClassOf', None)) : #Si jamais y'a pas de subClassOf, on entre pas ici
        liste_S.append(s)
        liste_O.append(o)
    for x in liste_S :
        for y in liste_O :
            if x == y: #On a un objet qui est aussi sujet, avec subClassOf en lien. Pas besoin de vérifier cas x vide
                s1, p, o1 = g.triples((None, 'http://www.w3.org/2000/01/rdf-schema#subClassOf', x))
                s2, p, o2 = g.triples((x, 'http://www.w3.org/2000/01/rdf-schema#subClassOf', None))
                s3, p, o3 = g.triples((s1, 'http://www.w3.org/2000/01/rdf-schema#subClassOf', o2))
                nbPossible += 1
                if s3 is not None :
                    a = a+1
	#return quelque chose
	
'''
On récupère ici l'objet o du triplet s p o tel que sujet3 predicat ?o. Provient de notre fichier d'exemple
'''


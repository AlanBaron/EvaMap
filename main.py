import sys
import os
import argparse
import rdflib
import pyaml
from rdflib.graph import Graph
import pprint
from pathlib import Path

def Consistency_subClassesProperties() :
	liste_S = []
	liste_O = []
	liste_Pg = []
	liste_Pd = []
	points = 0
	nbPossible = 0
	a = 0
	for s, _, o in g.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) : #Si jamais y'a pas de subClassOf, on entre pas ici
		liste_S.append(s)
		liste_O.append(o)
	for sp, _, so in g.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subPropertyOf'), None)) :
		liste_Pg.append(sp)
		liste_Pd.append(so)
	if len(liste_S) != 0 :	
		for x in liste_S :
			for y in liste_O :
				if x == y: #On a un objet qui est aussi sujet, avec subClassOf en lien. Pas besoin de vérifier cas x vide
				#Cas numéro 1 : transitivité subClassOf
					for s1, _, _ in g.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), x)) :
						for _, _, o1 in g.triples((x, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) :
							nbPossible = nbPossible + 1
							for _, p1, _ in g.triples((s1, None, o1)) :    
								if p1 == rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf') :
									a = a+1
				#Cas numéro 2 : A a B, B subClassOf C, A a C
				for s2, p2, _ in g.triples((None, None, x)) :
					for s3, _, _ in g.triples((s2, p2, y)) :
						nbPossible = nbPossible + 1;
						if s3 is not None :
							a = a + 1
	#Ici les subPropertyOf						
	if len(liste_Pg) != 0:
		for i in range(0,len(liste_Pg)-1) :
			for s4, _, o4 in g.triples((None, Pg[i], None)) :
				for s5, _, _ in g.triples((s4, Pd[i], o4)) :
					nbPossible = nbPossible + 1
					if s5 is not None :
						a = a + 1
						
	if nbPossible == 0 :
		return 0
	else :
		return a/nbPossible
	
parser = argparse.ArgumentParser()
parser.add_argument('file')
args = parser.parse_args()
#On regarde si le fichier existe
if os.path.exists(args.file)  :
	print("Files exist")
#On regarde si le fichier est un .rdf
	if Path(args.file).suffix == '.rdf' :
		with open(args.file) as file:
			g = Graph()
			g.parse(file)
		for s, p, o in g.triples((None, None, None)) :
			pprint.pprint(s)
			pprint.pprint(p)
			pprint.pprint(o)
		print(Consistency_subClassesProperties())
			
	


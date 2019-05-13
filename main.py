import sys
import os
import argparse
import rdflib
import pyaml
from rdflib.graph import Graph
import pprint
from pathlib import Path
import urllib
from SPARQLWrapper import SPARQLWrapper, XML


def Consistency_subClassesProperties() :
	liste_S = []
	liste_O = []
	liste_Pg = []
	liste_Pd = []
	points = 0
	nbPossible = 0
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
				#Cas numéro 1 : transitivité subClassOf (doit-on vraiment vérifier ça? Le cas 2 couvre ce cas normalement, en plus simple et plus optimiser... Y réfléchir)
					for s1, _, _ in g.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), x)) :
						for _, _, o1 in g.triples((x, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) :
							nbPossible = nbPossible + 1
							for _, p1, _ in g.triples((s1, None, o1)) :    
								if p1 == rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf') :
									points = points + 1
				#Cas numéro 2 : A a B, B subClassOf C, A a C
				for s2, p2, _ in g.triples((None, None, x)) :
					for s3, _, _ in g.triples((s2, p2, y)) :
						nbPossible = nbPossible + 1;
						if s3 is not None :
							points = points + 1
	#Ici les subPropertyOf						
	if len(liste_Pg) != 0:
		for i in range(0,len(liste_Pg)-1) :
			for s4, _, o4 in g.triples((None, Pg[i], None)) :
				for s5, _, _ in g.triples((s4, Pd[i], o4)) :
					nbPossible = nbPossible + 1
					if s5 is not None :
						points = points + 1
						
	if nbPossible == 0 :
		return 0
	else :
		return points/nbPossible
		
def Consistency_equivalentClassesProperties() :
	liste_S = []
	liste_O = []
	liste_Pg = []
	liste_Pd = []
	points = 0
	nbPossible = 0
	for s, _, o in g.triples((None, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentClass'), None)) :
		liste_S.append(s)
		liste_O.append(o)
	for sp, _, so in g.triples((None, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentProperty'), None)) :
		liste_Pg.append(sp)
		liste_Pd.append(so)
	if len(liste_S) != 0 :	
		for x in liste_S :
			for y in liste_O :
				for s2, p2, _ in g.triples((None, None, x)) :
					for s3, _, _ in g.triples((s2, p2, y)) :
						nbPossible = nbPossible + 1;
						if s3 is not None :
							points = points + 1
	if len(liste_Pg) != 0:
		for i in range(0,len(liste_Pg)-1) :
			for s4, _, o4 in g.triples((None, Pg[i], None)) :
				for s5, _, _ in g.triples((s4, Pd[i], o4)) :
					nbPossible = nbPossible + 1
					if s5 is not None :
						points = points + 1
						
	if nbPossible == 0 :
		return 0
	else :
		return points/nbPossible
		
def Consistency_disjointWith() :
	liste_S = []
	liste_O = []
	points = 0
	nbPossible = 0
	for s, _, o in g.triples((None, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith'), None)) :
		liste_S.append(s)
		liste_O.append(o)
	if len(liste_S) != 0 :	
		for x in liste_S :
			for y in liste_O :
				for s1, _, _ in g.triples((None,  rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), x)) :
					for _, p2, _ in g.triples((s1, None, y)) :
						nbPossible = nbPossible + 1
						if p2 is not None and p2 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
							points = points + 1
					for _, p7, _ in g.triples((y, None, s1)) :
						nbPossible = nbPossible + 1
						if p7 is not None and p7 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
							points = points + 1
				for _, p3, _ in g.triples((x, None, y)):
					nbPossible = nbPossible + 1
					if p3 is not None and p3 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
						points = points + 1
				for _, p4, _ in g.triples((y, None, x)):
					nbPossible = nbPossible + 1
					if p4 is not None and p4 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
						points = points + 1
				for s5, _, _ in g.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), y)) :
					for _, p6, _ in g.triples((s5, None, x)) :
						nbPossible = nbPossible + 1
						if p6 is not None and p6 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
							points = points + 1
					for _, p8, _ in g.triples((x, None, s5)) :
						nbPossible = nbPossible + 1
						if p8 is not None and p8 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
							points = points + 1
	if nbPossible == 0 :
		return 0
	else :
		return 0-(points/nbPossible)
	
def Conciseness_longURI() :
	nbPossible = 0
	points = 0
	for s, p, o in g.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			if len(p) >= 80 :
				points = points + 1
		if isinstance(p, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			if len(p) >= 80 :
				points = points + 1
		if isinstance(o, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			if len(p) >= 80 :
				points = points + 1
	print(nbPossible)
	print(points)
	if nbPossible == 0:
		return 0
	else :
		return 0-(points/nbPossible)
		
def Availability_Error() :
	nbPossible = 0
	points = 0
	for s, p, o in g.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			a = urllib.urlopen(s).getcode()
			if a >= 400 :
				points = points + 1
		if isinstance(p, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			a = urllib.urlopen(p).getcode()
			if a >= 400 :
				points = points + 1
		if isinstance(o, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			a = urllib.urlopen(o).getcode()
			if a >= 400 :
				points = points + 1
				
def Conciseness_duplicatedRules() :  #Oublier!!!
	nbPossible = 0
	points = 0
	liste_spo = []
	for s, p, o in g.triples((None, None, None)) :
		liste_spo.append((s, p, o))
	nbPossible = len(liste_spo)
	if nbPossible == 0 :
		return 0
	else : 
		return 0-(points/nbPossible)
		
def Consistency_domainRange() :
	nbPossible = 0
	points = 0
	liste_O = []
	for s, p, o in g.triples((None, None, None)) :
		for _, _, o2 in g.triples((p or None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#range'), None)) :
			nbPossible = nbPossible + 1
			for _, _, o3 in g.triples((s, rdflib.term.URIRef('a'), None)) :
				if o2 != o3 :
					liste_O.append(o3)
					for _, _, o4 in g.triples((o3, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentClass'), None)) :
						liste_O.append(o4)
					for O in liste_O :
						for _, _, o5 in g.triples((O, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) : #On considère le graphe comme complet ici. Transitivité des subclassOf, ... Donc un mauvais schéma peut pottentiellement perdre beaucoup de points
							if o2 != o5:
								points = points + 1
		liste_O = []			
		for _, _, o2 in g.triples((p, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#domain'), None))	:
			nbPossible = nbPossible + 1
			for _, _, o3 in ((o, rdflib.term.URIRef('a'), None)) :
				if o2 != o3 :
					liste_O.append(o3)
					for _, _, o4 in g.triples((o3, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentClass'), None)) :
						liste_O.append(o4)
					for O in liste_O :
						for _, _, o5 in g.triples((O, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) : #On considère le graphe comme complet ici. Transitivité des subclassOf, ... Donc un mauvais schéma peut pottentiellement perdre beaucoup de points
							if o2 != o5:
								points = points + 1
	if nbPossible == 0 :
		return 0
	else :
		return 0-(points/nbPossible)
				
			
		
		
#Ceci est le main... Voir comment bien le faire avec python
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
			pprint.pprint(p)
		print(Consistency_domainRange())
			
	
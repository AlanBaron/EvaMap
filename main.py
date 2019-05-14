import sys
import os
import argparse
import rdflib
import pyaml
from rdflib.graph import Graph
import pprint
from pathlib import Path
import urllib
from urllib.parse import urlparse

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
				#Cas numéro 1 : transitivité subClassOf (doit-on vraiment vérifier ça? Le cas 2 couvre ce cas normalement, en plus simple et plus optimisé... Y réfléchir)
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
	
def Clarity_HumanReadableURIs() : #A finir (comment dire que c'est human readable)
	nbPossible = 0
	points = 0
	for s, p, o in g.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			str = urlparse(s)
			if str.fragment != '' :
				str = str.fragment
				#tester str.fragment avec regex
			else : 
				str = str.path
				#regex sur ce qu'il y a après le dernier '/'
		if isinstance(p, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			str = urlparse(s)
			if str.fragment != '' :
				str = str.fragment
				#tester str.fragment avec regex
			else : 
				str = str.path
				#regex sur ce qu'il y a après le dernier '/'
		if isinstance(o, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			str = urlparse(s)
			if str.fragment != '' :
				str = str.fragment
				#tester str.fragment avec regex
			else : 
				str = str.path
				#regex sur ce qu'il y a après le dernier '/'
	if nbPossible == 0 :
		return 1
	else :
		return points/nbPossible

def Conciseness_duplicatedRules() :  #Oublier!!! Va falloir réussir à extraire les règles dupliquées, une fois fait le reste est ultra simple
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
	
	
def Clarity_humanDesc() : #Revoir le return
	nbPossible = 0
	points = 0
	liste_URIs = []
	for s, p, o in g.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			liste_URIs.append(s)
		if isinstance(p, rdflib.term.URIRef) :
			liste_URIs.append(p)
		if isinstance(o, rdflib.term.URIRef) :
			liste_URIs.append(o)
	for elt in liste_URIs :
		passe = False
		nbPossible = nbPossible + 1
		for s2, _, _ in g.triples((elt, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'), None)) :
			passe = True
		for s2, _, _ in g.triples((elt, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#comment'), None)) :
			passe = True
		if passe :
			points = points + 1

	return points

def Clarity_longTerm() :
	return 0
	#Une date dans chaque URI ? du regex

def Consistency_domainRange() :
	nbPossible = 0
	points = 0
	liste_O = []
	for s, p, o in g.triples((None, None, None)) :
		boolean = False
		for _, _, o2 in g.triples((p, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#range'), None)) :
			nbPossible = nbPossible + 1
			print(nbPossible)
			for _, _, o3 in g.triples((s, rdflib.term.URIRef('a'), None)) :
				pprint.pprint(o2)
				pprint.pprint(o3)
				if o2 != o3 :
					liste_O.append(o3)
					for _, _, o4 in g.triples((o3, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentClass'), None)) :
						liste_O.append(o4)
					for O in liste_O :
						for _, _, o5 in g.triples((O, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) : #On considère le graphe comme complet ici. Transitivité des subclassOf, ... Donc un mauvais schéma peut pottentiellement perdre beaucoup de points
							if o2 == o5:
								boolean = True
				else :
					boolean = True
			if not boolean :
				points = points + 1
		liste_O = []			
		for _, _, o2 in g.triples((p, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#domain'), None))	:
			nbPossible = nbPossible + 1
			print(nbPossible)
			for _, _, o3 in g.triples((s, rdflib.term.URIRef('a'), None)) :
				pprint.pprint(o2)
				pprint.pprint(o3)
				if o2 != o3 :
					liste_O.append(o3)
					for _, _, o4 in g.triples((o3, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentClass'), None)) :
						liste_O.append(o4)
					for O in liste_O :
						for _, _, o5 in g.triples((O, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) : #On considère le graphe comme complet ici. Transitivité des subclassOf, ... Donc un mauvais schéma peut pottentiellement perdre beaucoup de points
							if o2 == o5:
								boolean = True
				else :
					boolean = True
			if not boolean :
				points = points + 1
				
	if nbPossible == 0 :
		return 0
	else :
		print(points)
		print(nbPossible)
		return 0-(points/nbPossible)

def Interlinking_owlSameAs() :
	nbPossible = 0 
	points = 0
	liste_URIs = []
	for s, p, o in g.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			liste_URIs.append(s)
		if isinstance(o, rdflib.term.URIRef) :
			liste_URIs.append(o)
	for elt in liste_URIs :
		nbPossible = nbPossible + 1
		for _, _, o2 in g.triples((elt, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#sameAs'), None)) :
			points = points + 1
			if o2 in liste_URIs :
				liste_URIs.remove(o2)
		for s2, _, _ in g.triples((None, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#sameAs'), elt)) :
			points = points + 1
			if s2 in liste_URIs :
				liste_URIs.remove(s2)
	if nbPossible == 0 :
		return 0
	else :
		return points/nbPossible
		
	
def Interlinking_externalURIs() :
	return 0
	

def Interlinking_localLinks() : #Retrourne en quelque sorte le nombre d'îlots
	liste_value = []
	i = 1
	val_S = 0
	val_O = 0
	for s, _, o in g.triples((None, None, None)) :
		index_S = 0
		index_O = 0
		parc_S = False
		parc_O = False
		for elt in liste_value :
			if s in elt :
				val_S = elt[1]
				parc_S = True
				index_S = liste_value.index(elt)
			if o in elt :
				val_O = elt[1]
				parc_O = True
				index_S = liste_value.index(elt)
			if parc_S and parc_O :
				if val_S < val_O :
					liste_value[index_O][1] = val_S
					liste_value = Interlinking_localLinkNewCalc(liste_value, o, val_S)
				elif val_S > val_O :
					liste_value[index_S][1] = val_O
					liste_value = Interlinking_localLinkNewCalc(liste_value, s, val_O)
				break
		if parc_S and not parc_O :
			liste_value.append([o, val_S])
		elif parc_O and not parc_S :
			liste_value.append([s, val_O])
		elif not parc_O and not parc_S :
			liste_value.append([s, i])
			liste_value.append([o, i])
			i = i + 1
	nb = []
	for elt in liste_value :
		if elt[1] not in nb :
			nb.append(elt[1])
	return len(nb)
	

def Interlinking_localLinkNewCalc(liste, ref, value) :
	for _, _, o in g.triples((ref, None, None)) :
		for elt in liste :
			if o in elt :
				if elt[1] > value :
					elt[1] = value
					Interlinking_localLinkNewCalc(liste, o, value)
	for s, _, _ in g.triples((None, None, ref)) :
		for elt in liste :
			if s in elt :
				if elt[1] > value :
					elt[1] = value
					Interlinking_localLinkNewCalc(liste, s, value)
	return liste
	
def Interlinking_existingVocab() :
	return 0
	#ça... je cé pa

	
	
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
		#for s, p, o in g.triples((None, None, None)) :
		#	pprint.pprint(s)
		#	pprint.pprint(p)
		#	pprint.pprint(o)
		print(Interlinking_localLinks())
		
#Note : Réduire au max les répétitions avec des fonctions, tt ça. Code plus propre
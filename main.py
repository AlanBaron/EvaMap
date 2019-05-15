import sys
import os
import argparse
import rdflib
import pyaml
import yaml
import re
from rdflib.graph import Graph
import pprint
from pathlib import Path
import urllib
from urllib.parse import urlparse
from urllib.parse import urlsplit
import requests

def Consistency_subClassesProperties() :
	liste_S = []
	liste_O = []
	liste_Pg = []
	liste_Pd = []
	points = 0
	nbPossible = 0
	for s, _, o in g_map.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) : #Si jamais y'a pas de subClassOf, on entre pas ici
		liste_S.append(s)
		liste_O.append(o)
	for sp, _, so in g_map.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subPropertyOf'), None)) :
		liste_Pg.append(sp)
		liste_Pd.append(so)
	if len(liste_S) != 0 :	
		for x in liste_S :
			for y in liste_O :
				if x == y: #On a un objet qui est aussi sujet, avec subClassOf en lien. Pas besoin de vérifier cas x vide
				#Cas numéro 1 : transitivité subClassOf (doit-on vraiment vérifier ça? Le cas 2 couvre ce cas normalement, en plus simple et plus optimisé... Y réfléchir)
					for s1, _, _ in g_map.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), x)) :
						for _, _, o1 in g_map.triples((x, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) :
							nbPossible = nbPossible + 1
							for _, p1, _ in g_map.triples((s1, None, o1)) :    
								if p1 == rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf') :
									points = points + 1
				#Cas numéro 2 : A a B, B subClassOf C, A a C
				for s2, p2, _ in g_map.triples((None, None, x)) :
					for s3, _, _ in g_map.triples((s2, p2, y)) :
						nbPossible = nbPossible + 1;
						if s3 is not None :
							points = points + 1
	#Ici les subPropertyOf						
	if len(liste_Pg) != 0:
		for i in range(0,len(liste_Pg)-1) :
			for s4, _, o4 in g_map.triples((None, liste_Pg[i], None)) :
				for s5, _, _ in g_map.triples((s4, liste_Pd[i], o4)) :
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
	for s, _, o in g_link.triples((None, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentClass'), None)) :
		liste_S.append(s)
		liste_O.append(o)
	for sp, _, so in g_link.triples((None, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentProperty'), None)) :
		liste_Pg.append(sp)
		liste_Pd.append(so)
	if len(liste_S) != 0 :	
		for x in liste_S :
			for y in liste_O :
				for s2, p2, _ in g_link.triples((None, None, x)) :
					for s3, _, _ in g_link.triples((s2, p2, y)) :
						nbPossible = nbPossible + 1;
						if s3 is not None :
							points = points + 1
	if len(liste_Pg) != 0:
		for i in range(0,len(liste_Pg)-1) :
			for s4, _, o4 in g_link.triples((None, Pg[i], None)) :
				for s5, _, _ in g_link.triples((s4, Pd[i], o4)) :
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
	for s, _, o in g_link.triples((None, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith'), None)) :
		liste_S.append(s)
		liste_O.append(o)
	if len(liste_S) != 0 :	
		for x in liste_S :
			for y in liste_O :
				for s1, _, _ in g_link.triples((None,  rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), x)) :
					for _, p2, _ in g_link.triples((s1, None, y)) :
						nbPossible = nbPossible + 1
						if p2 is not None and p2 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
							points = points + 1
					for _, p7, _ in g_link.triples((y, None, s1)) :
						nbPossible = nbPossible + 1
						if p7 is not None and p7 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
							points = points + 1
				for _, p3, _ in g_link.triples((x, None, y)):
					nbPossible = nbPossible + 1
					if p3 is not None and p3 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
						points = points + 1
				for _, p4, _ in g_link.triples((y, None, x)):
					nbPossible = nbPossible + 1
					if p4 is not None and p4 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
						points = points + 1
				for s5, _, _ in g_link.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), y)) :
					for _, p6, _ in g_link.triples((s5, None, x)) :
						nbPossible = nbPossible + 1
						if p6 is not None and p6 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
							points = points + 1
					for _, p8, _ in g_link.triples((x, None, s5)) :
						nbPossible = nbPossible + 1
						if p8 is not None and p8 != rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith') :
							points = points + 1
	if nbPossible == 0 :
		return 0
	else :
		return 0-(points/nbPossible)
	
def Conciseness_longURI() : #Opérationnel ----------------------------------------------------------------
	nbPossible = 0
	points = 0
	for s, p, o in g_map.triples((None, None, None)) :
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
		
def Availability_Error() : #Corrigé, opérationelle, et optimisé au mieux --------------------------------------------------------------------------
	nbPossible = 0
	points = 0
	set_URIs = set()
	for s, p, o in g_map.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			set_URIs.add(str(s).split('$')[0])
		if isinstance(p, rdflib.term.URIRef) and p != rdflib.term.URIRef('a') :
			set_URIs.add(str(p).split('$')[0])
		if isinstance(o, rdflib.term.URIRef) :
			set_URIs.add(str(o).split('$')[0])			
	nbPossible = len(set_URIs)
	for elt in set_URIs :
		a = requests.get(elt)
		try :
			a.raise_for_status()
		except:
			points = points + 1
	if nbPossible == 0 :
		return 0
	else :
		return 0-(points/nbPossible)
	
def Clarity_HumanReadableURIs() : #A finir (comment dire que c'est human readable)
	nbPossible = 0
	points = 0
	for s, p, o in g_link.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			str = urlparse(s)
			if str.fragment != '' :
				str = str.fragment
				test_HumanReadable(str)
			else : 
				str = str.path
				str = str.split("/")[-1]
				test_HumanReadable(str)
		if isinstance(p, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			str = urlparse(p)
			if str.fragment != '' :
				str = str.fragment
				test_HumanReadable(str)
			else : 
				str = str.path
				str = str.split("/")[-1]
				test_HumanReadable(str)
		if isinstance(o, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			str = urlparse(o)
			if str.fragment != '' :
				str = str.fragment
				test_HumanReadable(str)
			else : 
				str = str.path
				str = str.split("/")[-1]
				test_HumanReadable(str)
	if nbPossible == 0 :
		return 1
	else :
		return points/nbPossible
		
def test_HumanReadable(str) :
	print(str)
	str2 = re.match('[A-Z][A-Z][A-Z]', str)
	if str2 is not None :
		return str2
	str2 = re.match('[0-9]+[A-Za-z0-9\-\_]+$', str)
	print(str2)
	return str2

def Conciseness_duplicatedRules() :  #Oui, passé des heures dessus pour au final avoir ça... Revoir le score --------------------------------------------------
	return len(liste_map) - len(g_map)
	
	
def Clarity_humanDesc() : #Revoir le return, opérationnel sinon -------------------------------------------------
	nbPossible = 0
	points = 0
	set_URIs = set()
	for s, p, o in g_map.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			set_URIs.add(s)
		if isinstance(p, rdflib.term.URIRef) and p != rdflib.term.URIRef('a') :
			set_URIs.add(p)
		if isinstance(o, rdflib.term.URIRef) :
			set_URIs.add(o)
	for elt in set_URIs :
		passe = False
		nbPossible = nbPossible + 1
		for s2, _, _ in g_link.triples((elt, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'), None)) :
			passe = True
		for s2, _, _ in g_link.triples((elt, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#comment'), None)) :
			passe = True
		if passe :
			points = points + 1
	return points

def Clarity_longTerm() : #Complété, corrigé et fonctionnel. Revoir le return ? -----------------------------------------------------
	nbPossible = 0
	points = 0
	set_URIs = set()
	for s, p, o in g_map.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			set_URIs.add(s)
		if isinstance(p, rdflib.term.URIRef) :
			set_URIs.add(p)
		if isinstance(o, rdflib.term.URIRef) :
			set_URIs.add(o)
	for elt in set_URIs :
		nbPossible = nbPossible + 1
		splitted_elt = elt.split('/')
		for elements in splitted_elt :
			try :
				if int(elements) > 1990 and int(elements) < 2050 :
					points = points + 1
			except ValueError :
				pass
	if nbPossible == 0 :
		return 0
	else :
		return points/nbPossible

def Consistency_domainRange() :
	nbPossible = 0
	points = 0
	liste_O = []
	for s, p, o in g_link.triples((None, None, None)) :
		boolean = False
		for _, _, o2 in g_link.triples((p, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#range'), None)) :
			nbPossible = nbPossible + 1
			print(nbPossible)
			for _, _, o3 in g_link.triples((s, rdflib.term.URIRef('a'), None)) :
				pprint.pprint(o2)
				pprint.pprint(o3)
				if o2 != o3 :
					liste_O.append(o3)
					for _, _, o4 in g_link.triples((o3, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentClass'), None)) :
						liste_O.append(o4)
					for O in liste_O :
						for _, _, o5 in g_link.triples((O, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) : #On considère le graphe comme complet ici. Transitivité des subclassOf, ... Donc un mauvais schéma peut pottentiellement perdre beaucoup de points
							if o2 == o5:
								boolean = True
				else :
					boolean = True
			if not boolean :
				points = points + 1
		liste_O = []			
		for _, _, o2 in g_link.triples((p, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#domain'), None))	:
			nbPossible = nbPossible + 1
			print(nbPossible)
			for _, _, o3 in g_link.triples((s, rdflib.term.URIRef('a'), None)) :
				pprint.pprint(o2)
				pprint.pprint(o3)
				if o2 != o3 :
					liste_O.append(o3)
					for _, _, o4 in g_link.triples((o3, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentClass'), None)) :
						liste_O.append(o4)
					for O in liste_O :
						for _, _, o5 in g_link.triples((O, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) : #On considère le graphe comme complet ici. Transitivité des subclassOf, ... Donc un mauvais schéma peut pottentiellement perdre beaucoup de points
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
	for s, p, o in g_link.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			liste_URIs.append(s)
		if isinstance(o, rdflib.term.URIRef) :
			liste_URIs.append(o)
	for elt in liste_URIs :
		nbPossible = nbPossible + 1
		for _, _, o2 in g_link.triples((elt, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#sameAs'), None)) :
			points = points + 1
			if o2 in liste_URIs :
				liste_URIs.remove(o2)
		for s2, _, _ in g_link.triples((None, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#sameAs'), elt)) :
			points = points + 1
			if s2 in liste_URIs :
				liste_URIs.remove(s2)
	if nbPossible == 0 :
		return 0
	else :
		return points/nbPossible
		
	
def Interlinking_externalURIs() :
	return 0
	

def Interlinking_localLinks() : #Retrourne en quelque sorte le nombre d'îlots. Opérationnel --------------------------------------------------------------------
	liste_value = []
	i = 1
	val_S = 0
	val_O = 0
	for s, _, o in g_map.triples((None, None, None)) :
		pprint.pprint(s)
		pprint.pprint(o)
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
	

def Interlinking_localLinkNewCalc(liste, ref, value) : #Utilisé pour la méthode précédente uniquement
	for _, _, o in g_link.triples((ref, None, None)) :
		for elt in liste :
			if o in elt :
				if elt[1] > value :
					elt[1] = value
					Interlinking_localLinkNewCalc(liste, o, value)
	for s, _, _ in g_link.triples((None, None, ref)) :
		for elt in liste :
			if s in elt :
				if elt[1] > value :
					elt[1] = value
					Interlinking_localLinkNewCalc(liste, s, value)
	return liste
	
def Interlinking_existingVocab() :
	return 0
	#ça... je cé pa

def yamlToTriples(mapping) : #Opérationnel ! ------------------------------------------------------------------------------------
	liste_map = []
	for name in mapping["mappings"] :
		for predicateobject in mapping["mappings"][name]["predicateobjects"] :
			if len(predicateobject) == 2 :
				if re.search('(http://)|(https://)', predicateobject[1]) is not None :
					liste_map.append([rdflib.term.URIRef(mapping["mappings"][name]["subject"]), rdflib.term.URIRef(predicateobject[0]), rdflib.term.URIRef(predicateobject[1])])
				else : 
					liste_map.append([rdflib.term.URIRef(mapping["mappings"][name]["subject"]), rdflib.term.URIRef(predicateobject[0]), rdflib.term.Literal(predicateobject[1])])
			elif len(predicateobject) == 3 :
				if len(predicateobject[2].split('~')) == 2 :
					if predicateobject[2].split('~')[1] == 'lang' :
						liste_map.append([rdflib.term.URIRef(mapping["mappings"][name]["subject"]), rdflib.term.URIRef(predicateobject[0]), rdflib.term.Literal(predicateobject[1], lang = predicateobject[2].split('~')[0])])
					else :
						liste_map.append([rdflib.term.URIRef(mapping["mappings"][name]["subject"]), rdflib.term.URIRef(predicateobject[0]), rdflib.term.Literal(predicateobject[1], datatype = predicateobject[2])])
				else :
					liste_map.append([rdflib.term.URIRef(mapping["mappings"][name]["subject"]), rdflib.term.URIRef(predicateobject[0]), rdflib.term.Literal(predicateobject[1], datatype = predicateobject[2])])
	#on relie les variables aux mappings correspondant, jusque là considérées comme des litérals
	for name in mapping["mappings"] :
		for triples in liste_map :
			if str(triples[2]) == name :
				triples[2] = rdflib.term.URIRef(mapping["mappings"][name]["subject"])
	return liste_map
	
if __name__ == '__main__':
	#regarder ici plus tard si on a bien 3 arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('file1')
	parser.add_argument('file2')
	args = parser.parse_args()

	#On regarde si les fichiers existent
	if os.path.exists(args.file1) and os.path.exists(args.file2) :
		print("Files exist")
		g_onto = Graph()
		g_link = Graph()
		g_map = Graph()
	#On regarde le type des fichiers
		if Path(args.file1).suffix == '.rdf' :
			with open(args.file1) as file:
				g_link.parse(file)
				g_onto = g_link
			if Path(args.file2).suffix == '.yml' : #Penser au JSON pour après !!!
				with open(args.file2) as file2 :
					mapping = yaml.load(file2, Loader=yaml.FullLoader)
					liste_map = yamlToTriples(mapping)
		elif Path(args.file2).suffix == '.rdf' :
			with open(args.file) as file:
				g_link.parse(file)
				g_onto = g_link
			if Path(args.file1).suffix == '.yml' : #Penser au JSON pour après !!!
				with open(args.file2) as file2 :
					mapping = yaml.load(file2, Loader=yaml.FullLoader)
					liste_map = yamlToTriples(mapping)
					
		for triple in liste_map :
			g_link.add(triple)
			g_map.add(triple)
		#for s, p, o in g_map.triples((None, None, None)) :
		#		pprint.pprint(o)
		print(Conciseness_duplicatedRules())
		
	else : 
		print('Les fichiers n\'existent pas')
	#Note : Réduire au max les répétitions avec des fonctions, tt ça. Code plus propre
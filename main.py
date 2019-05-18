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
import requests
import json

def Consistency_subClassesProperties() : #Même remarque que la suivante. Fonctionne ----------------------------
	set_SO = set()
	set_P = set()
	points = 0
	nbPossible = 0
	for s, p, o in g_map.triples((None, None, None)) :
		set_SO.add(s)
		set_SO.add(o)
		set_P.add(p)
	for subobj in set_SO :
		for _, _, o2 in g_onto.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), subobj)) :
			if not isinstance(o2, rdflib.term.BNode) :
				nbPossible = nbPossible + 1
			if (None, None, o2) in g_map and not isinstance(o2, rdflib.term.BNode):
				points = points + 1
			elif (o2, None, None) in g_map and not isinstance(o2, rdflib.term.BNode):
				points = points + 1
	for pred in set_P :	
		for _, _, o3 in g_onto.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subPropertyOf'), pred)) :
			if not isinstance(o3, rdflib.term.BNode) :
				nbPossible = nbPossible + 1
			if (None, o3, None) in g_map and not isinstance(o3, rdflib.term.BNode) :
				points = points + 1					
	if nbPossible == 0 :
		return 1
	else :
		return points/nbPossible
		
def Consistency_equivalentClassesProperties() : #Ici on considère que si une classe equivalente est dans notre mapping, alors elle est correctement utilisée. Corrigé
	set_SO = set()
	set_P = set()
	points = 0
	nbPossible = 0
	for s, p, o in g_map.triples((None, None, None)) :
		set_SO.add(s)
		set_SO.add(o)
		set_P.add(p)
	for subobj in set_SO :
		for _, _, o2 in g_onto.triples((subobj, rdflib.term.URIRef('http://www.w3.org/2002/07/owl#equivalentClass'), None)) :
			if not isinstance(o2, rdflib.term.BNode) :
				nbPossible = nbPossible + 1
			if (None, None, o2) in g_map and not isinstance(o2, rdflib.term.BNode):
				points = points + 1
			elif (o2, None, None) in g_map and not isinstance(o2, rdflib.term.BNode):
				points = points + 1
	for pred in set_P :	
		for _, _, o3 in g_onto.triples((pred, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentProperty'), None)) :
			nbPossible = nbPossible + 1
			if (None, None, o3) in g_map and not isinstance(o3, rdflib.term.BNode) :
				points = points + 1
			elif (o3, None, None) in g_map and not isinstance(o3, rdflib.term.BNode):
				points = points + 1
						
	if nbPossible == 0 :
		return 1
	else :
		return points/nbPossible
		
def Consistency_disjointWith() : #Corrigé, devrait fonctionner -----------------------------------------------
	points = 0
	nbPossible = 0
	for s, _, o in g_map.triples((None, None, None)) :
		nbPossible = nbPossible + 1
		for _, _, o1 in g_onto.triples((s, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith'), None)) :
			if g_onto.triples((o, (rdflib.term.URIRef('a')|rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')), o1)) is not None :
				points = points + 1
			else :
				for s1, _, _ in g_onto.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf') ,o)):
					if g_onto.triples((s1, (rdflib.term.URIRef('a')|rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')), o1)) is not None :
						points = points + 1
		for _, _, o1 in g_onto.triples((o, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#disjointWith'), None)) :
			if g_onto.triples((s, (rdflib.term.URIRef('a')|rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')), o1)) is not None :
				points = points + 1
			else :
				for s1, _, _ in g_onto.triples((None, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf') ,s)):
					if g_onto.triples((s1, (rdflib.term.URIRef('a')|rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')), o1)) is not None :
						points = points + 1
		
	if nbPossible == 0 :
		return 1
	else :
		return 1-points/nbPossible
	
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
		return 1
	else :
		return 1-points/nbPossible
		
def Availability_Error() : #Corrigé, opérationelle, et optimisé au mieux --------------------------------------------------------------------------
	nbPossible = 0
	points = 0
	set_URIs = set()
	for s, p, o in g_map.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			str1 = str(s)
			str2 = str(s)
			str1 = str1.split('$')[0].split('#')[0]
			if str1 == str2 :
				str1 = str1.rsplit('/', 1)[0] + '/'
			set_URIs.add(str1)
		if isinstance(p, rdflib.term.URIRef) and p != rdflib.term.URIRef('a') :
			str1 = str(p)
			str2 = str(p)
			str1 = str1.split('$')[0].split('#')[0]
			if str1 == str2 :
				str1 = str1.rsplit('/', 1)[0] + '/'
			set_URIs.add(str1)
		if isinstance(o, rdflib.term.URIRef) :
			str1 = str(o)
			str2 = str(o)
			str1 = str1.split('$')[0].split('#')[0]
			if str1 == str2 :
				str1 = str1.rsplit('/', 1)[0] + '/'
			set_URIs.add(str1)	
	nbPossible = len(set_URIs)
	for elt in set_URIs :
		a = requests.get(elt)
		try :
			a.raise_for_status()
		except:
			points = points + 1
	if nbPossible == 0 :
		return 1
	else :
		return 1-points/nbPossible
	
def Clarity_HumanReadableURIs() : #Complet --------------------------------------------------------------------------------
	nbPossible = 0
	points = 0
	for s, p, o in g_map.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			str = urlparse(s)
			if str.fragment != '' :
				str = str.fragment
				if test_HumanReadable(str) :
					points = points + 1
			else : 
				str = str.path
				str = str.split("/")[-1]
				if test_HumanReadable(str) :
					points = points + 1
		if isinstance(p, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			str = urlparse(p)
			if str.fragment != '' :
				str = str.fragment
				if test_HumanReadable(str) :
					points = points + 1
			else : 
				str = str.path
				str = str.split("/")[-1]
				if test_HumanReadable(str) :
					points = points + 1
		if isinstance(o, rdflib.term.URIRef) :
			nbPossible = nbPossible + 1
			str = urlparse(o)
			if str.fragment != '' :
				str = str.fragment
				if test_HumanReadable(str) :
					points = points + 1
			else : 
				str = str.path
				str = str.split("/")[-1]
				if test_HumanReadable(str) :
					points = points + 1
	if nbPossible == 0 :
		return 1
	else :
		return 1-((nbTriples*3) - points)/(nbTriples*3)
		
def test_HumanReadable(str) : #------------------------ Utilisé au dessus --------------------------------------------------
	regexp = re.compile(r'[A-Z][A-Z][A-Z]') #Si on a une suite de 3 majuscules
	if regexp.search(str):
		return False
	regexp = re.compile(r'[0-9]+[A-Za-z-_.]+[0-9]*$') #Si on a un string contenant un chiffre au milieu d'autre caractères
	if regexp.search(str):
		return False
	regexp = re.compile(r'[$+!*\'()]') #Si on a un caractère particulier qui ne devrait pas exister
	if regexp.search(str):
		return False
	if len(str) < 3 : #si la taille est inférieure à 3
		return False
	if re.subn('[0-9]', '', str)[1] > 8 : #Si on a plus de 8 chiffres (date)
		return False
	return True

def Conciseness_duplicatedRules() :  #Oui, passé des heures dessus pour au final avoir ça... Revoir le score --------------------------------------------------
	return len(g_map)/len(liste_map)
	
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
	return points/(nbTriples*3)
	
def Clarity_longTerm() : #Complété, corrigé et fonctionnel. Revoir le return ? -----------------------------------------------------
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
		nbPossible = nbPossible + 1
		splitted_elt = elt.split('/')
		for elements in splitted_elt :
			try :
				if int(elements) > 1990 and int(elements) < 2050 :
					points = points + 1
			except ValueError :
				pass
	if nbPossible == 0 :
		return 1
	else :
		return points/(nbTriples*3)

def Consistency_domainRange() : #Il est bon de noter ici qu'un mapping avec peu de lien externes peut potentiellement donner une mauvaise note, sans pour autant être mauvais
#Cas des littéraux avec datatype non pris en compte! A voir si y'a le temps
	nbPossible = 0
	points = 0
	liste_O = []
	for s, p, o in g_map.triples((None, None,None)) :
		nbPossible = nbPossible + 2
		boolean = False
		if p == rdflib.term.URIRef('a') :
			p = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
		for _, _, o2 in g_link.triples((p, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#domain'), None)) : #Pour toutes les valeurs domain de p
			for _, _, o3 in g_link.triples((s, (rdflib.term.URIRef('a')|rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')), None)) : #On récupère le type du sujet
				if o2 != o3 and o2 != rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Resource') : #Si le domaine de p est différent du type du sujet et que, cas général, le domaine de p n'est pas une ressource
					liste_O.append(o3)	#On stock le type du sujet
					for _, _, o4 in g_link.triples((s, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentClass'), None)): #Pour tous les équivalents au sujet
						for _, _, o6 in g_link.triples((s, (rdflib.term.URIRef('a')|rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')), None)) : #On récupère les type des sujets equivalents
							liste_O.append(o4) #On stock ces types aussi
					for O in liste_O : #Pour l'ensemble des types récupérés
						for _, _, o5 in g_link.triples((O, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) : #on regarde pour toutes les sous-classes des types (équivalents ou non) de notre sujet
							if o2 == o5: #Si ils sont équivalents au domaine
								boolean = True
				else :
					boolean = True
		if boolean :
			points = points + 1
		liste_O = []
		boolean = False
		for _, _, o2 in g_link.triples((p, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#range'), None))	:
			if o2 == rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Resource') :
				boolean = True
			if o2 == rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Literal') :
				if isinstance(o, rdflib.term.Literal) :
					boolean = True
			if isinstance(o, rdflib.term.URIRef) :
				for _, _, o3 in g_link.triples((o, (rdflib.term.URIRef('a')|rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')), None)) : #On récupère le type du sujet
					if o2 != o3 : #Si le domaine de p est différent du type du sujet et que, cas général, le domaine de p n'est pas une ressource
						liste_O.append(o3)	#On stock le type du sujet
						for _, _, o4 in g_link.triples((s, rdflib.term.URIRef('https://www.w3.org/2002/07/owl#equivalentClass'), None)): #Pour tous les équivalents au sujet
							for _, _, o6 in g_link.triples((s, (rdflib.term.URIRef('a')|rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')), None)) : #On récupère les type des sujets equivalents
								liste_O.append(o4) #On stock ces types aussi
						for O in liste_O : #Pour l'ensemble des types récupérés
							for _, _, o5 in g_link.triples((O, rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'), None)) : #on regarde pour toutes les sous-classes des types (équivalents ou non) de notre sujet
								if o2 == o5: #Si ils sont équivalents au domaine
									boolean = True
					else :
						boolean = True
		if boolean :
			points = points + 1
				
	if nbPossible == 0 :
		return 1
	else :
		return 1-((nbPossible) - points)/(nbPossible)

def Interlinking_owlSameAs() : #Corrigé, devrait être opérationnel. Ici, on regarde pour chaque URI si cette dernière à un owl:sameAs existant. --------------------------------------
	nbPossible = 0 
	points = 0
	set_URIs = set()
	for s, p, o in g_map.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) :
			set_URIs.add(s)
		if isinstance(o, rdflib.term.URIRef) :
			set_URIs.add(o)
		if isinstance(p, rdflib.term.URIRef) and p != rdflib.term.URIRef('a') :
			set_URIs.add(p)
	for elt in set_URIs :
		nbPossible = nbPossible + 1
		for _, _, o2 in g_link.triples((elt, rdflib.term.URIRef('http://www.w3.org/2002/07/owl#sameAs'), None)) :
			if o2 != elt :
				points = points + 1
		for s2, _, _ in g_link.triples((None, rdflib.term.URIRef('http://www.w3.org/2002/07/owl#sameAs'), elt)) :
			if s2 != elt :
				points = points + 1
	if nbPossible == 0 :
		return 1
	else :
		return points/(nbTriples*3)
	
def Interlinking_externalURIs() : #Revoir le return, sinon complet
	points = 0
	nbPossible = 0 
	for s, _, o in g_map.triples((None, None, None)) :
		if isinstance(s, rdflib.term.URIRef) and isinstance(o, rdflib.term.URIRef) : #Donc on a un lien entre deux URIs
			nbPossible = nbPossible + 1
			if not (s, None, o) in g_onto : #Et si ça n'existe pas dans notre ontologie, alors on a créé un nouveau lien
				points = points + 1
	if nbPossible == 0 :
		return 1
	else :
		return points/nbPossible
	
def Interlinking_localLinks() : #Retrourne en quelque sorte le nombre d'îlots. Opérationnel --------------------------------------------------------------------
	liste_value = []
	i = 1
	val_S = 0
	val_O = 0
	for s, _, o in g_map.triples((None, None, None)) :
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
	#ça... comment faire ?

def Coverage_Vertical() : #Fait ------------------------------------------------------
	set_dollarVal = set()
	correspondance = 0
	regexp = re.compile('\(([^)]+)') 
	for s, _, o in g_map.triples((None, None, None)) :
		if regexp.search(str(s)) is not None:
			set_dollarVal.add(re.search('\(([^)]+)', str(s)).group(1))
		if regexp.search(str(o)) is not None:
			set_dollarVal.add(re.search('\(([^)]+)', str(o)).group(1))
	if len(raw_data[0]['fields']) == 0 :
		return 1
	else :		
		return len(set_dollarVal)/len(raw_data[0]['fields'])

def Availability_localLink() : #qu'est-ce qu'un lien local ?
	return 0
	
def Availability_externalLink() : #qu'est-ce qu'un lien externe ?
	return 0
	
def Consistency_datatypeRange() : #Couvrir seulement les cas de nos mappings ! C'est à dire integer vs PositiveInteger, et datetime
	points = 0
	nbPossible = 0
	boolean = False
	for _, _, o in g_map.triples((None, None, None)) :
		if isinstance(o, rdflib.term.Literal) :
			nbPossible = nbPossible + 1
			if o.datatype is not None :
				if o.datatype == rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#positiveInteger') :
					string = re.search('\(([^)]+)', str(o)).group(1)
					for i in range(0, len(raw_data)) :
						if raw_data[0]['fields'][string] < 1 :
							boolean = True
					if boolean :
						points = points + 1
						boolean = False
				if o.datatype == rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer') : #ça devrait être un positiveInteger
					string = re.search('\(([^)]+)', str(o)).group(1)
					for i in range(0, len(raw_data)) :
						if raw_data[0]['fields'][string] < 1 :
							boolean = True
					if not boolean :
						points = points + 1
			else : #si y'a pas de type c'est moins bien
				points = points + 1
	return 1-points/nbPossible
		
def Facade(liste_poids) :
	total = 0
	total2 = 0
	points = []
	points.append(liste_poids[0] * Availability_Error())
#	print(points[0])
	points.append(liste_poids[1] * Clarity_humanDesc())
#	print(points[1])
	points.append(liste_poids[2] * Clarity_HumanReadableURIs())
#	print(points[2])
	points.append(liste_poids[3] * Clarity_longTerm())
#	print(points[3])
	points.append(liste_poids[4] * Conciseness_duplicatedRules())
#	print(points[4])
	points.append(liste_poids[5] * Conciseness_longURI())
#	print(points[5])
	points.append(liste_poids[6] * Consistency_domainRange())
#	print(points[6])
	points.append(liste_poids[7] * Consistency_subClassesProperties())
#	print(points[7])
	points.append(liste_poids[8] * Consistency_equivalentClassesProperties())
#	print(points[8])
	points.append(liste_poids[9] * Consistency_disjointWith())
#	print(points[9])
	points.append(liste_poids[10] * Interlinking_owlSameAs())
#	print(points[10])
	points.append(liste_poids[11] * Interlinking_externalURIs())
#	print(points[11])
	points.append(liste_poids[12] * Interlinking_localLinks())
#	print(points[12])
#	points.append(liste_poids[13] * Interlinking_existingVocab())
#	print(points[13])
#	points.append(liste_poids[14] * Availability_externalLink())
#	print(points[14])
#	points.append(liste_poids[15] * Availability_localLink())
#	print(points[15])
	points.append(liste_poids[13] * Consistency_datatypeRange())
#	print(points[13])
	points.append(liste_poids[14] * Coverage_Vertical())
#	print(points[14])
	
	for i in range(0,14):
		total = total + points[i]
		total2 = liste_poids[i] + total2
	print(total/total2)
	
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
	parser.add_argument('file3')
	args = parser.parse_args()
	#On regarde si les fichiers existent
	if os.path.exists(args.file1) and os.path.exists(args.file2) and os.path.exists(args.file3):
		print("Files exist")
		g_onto = Graph()
		g_link = Graph()
		g_map = Graph()
	else : 
		print('Les fichiers n\'existent pas')
		exit()
	files = []
	files.append(args.file1)
	files.append(args.file2)
	files.append(args.file3)
	for file in files :
		if Path(file).suffix == '.rdf' :
			g_onto.parse(open(file))
			for s, p, o in g_onto.triples((None, None, None)) :
				g_link.add((s, p, o))
		elif Path(file).suffix == '.yml' : #Penser au JSON pour après !!!
			mapping = yaml.load(open(file), Loader=yaml.FullLoader)
			liste_map = yamlToTriples(mapping)
		elif Path(file).suffix == '.json' :
			raw_data = json.load(open(file))
			#pprint.pprint(raw_data[0]["fields"])
		else :
			print('You should have a .rdf, .yml and a .json')
			exit()
	nbTriples = 0
	for triple in liste_map :
		nbTriples = nbTriples + 1
		g_link.add(triple)
		g_map.add(triple)
	#for s, p, o in g_onto.triples((None,None,None)) :
	#		print('---------------------')
	#		pprint.pprint(p)
	#		pprint.pprint(o)
	chose = [4, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 4, 3]
	Facade(chose)

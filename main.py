import sys
import os
import argparse
import rdflib
import pyaml
from rdflib.graph import Graph

parser = argparse.ArgumentParser()
parser.add_argument('rdf_file')
parser.add_argument('yaml_file')
parser.add_argument('json_file')
args = parser.parse_args()
if os.path.exists(args.rdf_file) and os.path.exists(args.yaml_file) and os.path.exists(args.json_file) :
	print("Files exist")
	print(args)
	
	with open(args.rdf_file) as rdf_file:
		g = Graph()
		g.parse(rdf_file)
		len(g)
		import pprint
		for stmt in g:
			pprint.pprint(stmt)
	
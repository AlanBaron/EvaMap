# EvaMap

Works under Python 3.7, and using rdflib, pyaml, argparse, pathlib & requests libraries

Gives a score of a mapping quality. 

# Prerequisite
  
Python 3.7 should be installed on your computer.

If you are using pip, execute the following commands :

```
pip install rdflib
```
```
pip install pyaml
```
```
pip install argparse
```
```
pip install requests
```
```
pip install yaml
```
```
pip install pathlib
```

After that, just use the following command line to obtain the mapping quality score :

```
python main.py ontologies.rdf mapping.yml raw_data.json
```

The ontologies.rdf file should contain informations about the ontologies of your mapping. It should be a classic rdf file (xml, turtle, ...)

The mapping.yml file should look like this, containing the mapping keyword, the name of the mapping, a subject and a predicateobjects.
```
mappings:
  name:
    subject: URI
    predicateobjects:
    - [a, 'ontology'(ex : 'http://www.w3.org/2000/01/rdf-schema#label')  or a literal (ex : 'hello world') or a reference (ex : $(column)]
    - [predicate, object]
  name2:
    ...
 ```
 
 The raw_data.json is a classic .json file.

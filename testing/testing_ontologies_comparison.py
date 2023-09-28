'''########################### COMPARING TWO ONTOLGIES SECTION BY SECTION ##############################################'''

import re
from lxml import etree
import difflib


def extract_sections_from_rdf(rdf_string):
    # Extract doctype section using regex
    doctype_section = re.search('<!DOCTYPE rdf:RDF \[.*?\]>', rdf_string, re.DOTALL)
    doctype_section = doctype_section.group() if doctype_section else 'Not found'
    print(doctype_section)
    # Convert string to bytes
    rdf_bytes = bytes(rdf_string, encoding='utf-8')
    # Parse RDF string to an XML object
    root = etree.fromstring(rdf_bytes)
    # Extract namespaces
    namespaces = root.nsmap

    print(namespaces)
    # Extract RDF section (uris definitions)

    # Extract class definitions
    class_definitions = [etree.tostring(e, pretty_print=True).decode() for e in root.findall('.//{http://www.w3.org/2002/07/owl#}Class')]
    # Extract object property definitions
    object_property_definitions = [etree.tostring(e, pretty_print=True).decode() for e in root.findall('.//{http://www.w3.org/2002/07/owl#}ObjectProperty')]
    # Extract data property definitions
    data_property_definitions = [etree.tostring(e, pretty_print=True).decode() for e in root.findall('.//{http://www.w3.org/2002/07/owl#}DatatypeProperty')]
    # Extract annotation definitions
    annotation_definitions = [etree.tostring(e, pretty_print=True).decode() for e in root.findall('.//{http://www.w3.org/2002/07/owl#}Ontology')]

    rdf_sections = {'doctype_section': doctype_section,
                    'rdf_section': None,
                    'namespaces': {uri.split(':')[0]: "".join(uri.split(':')[1:]) for uri in namespaces},
                    'class_definitions': class_definitions,
                    'object_property_definitions': object_property_definitions,
                    'data_property_definitions': data_property_definitions,
                    'annotation_definitions': annotation_definitions}

    rdf_sections['rdf_section'] = rdf_sections['namespaces']

    return rdf_sections


def dict_to_rdf(rdf_sections):
    # Initialize root element
    root = etree.Element('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF', rdf_sections['rdf_section'], nsmap=rdf_sections['namespaces'])

    # Helper function to add children to root
    def add_children(items):
        for item in items:
            child = etree.fromstring(item)
            root.append(child)

    # Add class definitions
    add_children(rdf_sections['class_definitions'])

    # Add object property definitions
    add_children(rdf_sections['object_property_definitions'])

    # Add data property definitions
    add_children(rdf_dict['data_property_definitions'])

    # Add annotation definitions
    add_children(rdf_sections['annotation_definitions'])

    # Convert root to string and prepend doctype
    rdf_string = f'{rdf_sections["doctype_section"][0]}\n{etree.tostring(root, pretty_print=True).decode()}'

    return rdf_string


def find_most_similar_section(section, sections):
    best_match = None
    best_ratio = 0

    for s in sections:
        seq = difflib.SequenceMatcher(None, section, s)
        ratio = seq.ratio()

        if ratio > best_ratio:
            best_ratio = ratio
            best_match = s

    return best_match, best_ratio

def compare_sections(section1, section2):

    d = difflib.Differ()
    diff = list(d.compare(section1.splitlines(), section2.splitlines()))

    # Count the lines that are only in each section
    only_in_section1 = sum(1 for line in diff if line.startswith('- '))
    only_in_section2 = sum(1 for line in diff if line.startswith('+ '))

    # Determine which section is more complete
    if only_in_section1 > only_in_section2:
        more_complete = 'section1'
    elif only_in_section1 < only_in_section2:
        more_complete = 'section2'
    else:
        more_complete = 'equal'

    return '\n'.join(diff), more_complete

from urllib.parse import urlparse
from rdflib import Graph, RDF

def get_type_and_name(rdf_string):
    g = Graph()
    g.parse(data=rdf_string, format='xml')

    # Assumes the graph contains a single RDF resource
    for s, p, o in g:
        if p == RDF.type:
            rdf_type = urlparse(o).fragment  # get the fragment part of the URI
            name = urlparse(s).fragment  # get the fragment part of the URI
            return rdf_type, name
    return None, None

def check_types_and_names(type_name1, type_name2):
    return True if type_name1 == type_name2 else False


# Extract sections from the two RDF/XML strings
sections1 = extract_sections_from_rdf(rdf_string1)
sections2 = extract_sections_from_rdf(rdf_string2)


rdf_dict = {
        'doctype_section': [],
        'rdf_section': [],
        'namespaces':[],
        'class_definitions': [],
        'object_property_definitions': [],
        'data_property_definitions': [],
        'annotation_definitions': []
    }

# Compare each section in the first document with the most similar section in the second document
for k, section1 in sections1.items():
    print(k,  type(section1))

    if k == 'doctype_section':
        section1 = [section1]
        section2 = [sections2[k]]
    elif k == 'namespaces':
        section1 = [key + ':' + value for key,value in section1.items()]
        section2 = [key + ':' + value for key,value in sections2[k].items()]
    else:
        section2 = sections2[k]


    for entity in section1:
        print(entity)

        # Find the most similar section in the second document
        best_match, best_ratio = find_most_similar_section(entity, section2)

        # Compare the sections
        if best_match is not None:
            if isinstance(entity, list) and len(entity) > 0:
                entity = entity[0]
            if isinstance(best_match, list) and len(best_match) > 0:
                best_match = best_match[0]

            diff, more_complete = compare_sections(entity, best_match)

            try:
                equal_type_name = check_types_and_names(
                    get_type_and_name(entity),
                    get_type_and_name(best_match)
                )
            except:
                equal_type_name = True

            if equal_type_name and more_complete == 'section1':
                rdf_dict[k].append(entity)
            elif equal_type_name and more_complete == 'section2':
                rdf_dict[k].append(best_match)
            elif equal_type_name and more_complete == 'equal':
                rdf_dict[k].append(entity)
            elif not equal_type_name:
                rdf_dict[k].append(entity)
                rdf_dict[k].append(best_match)

            print('########## output #################')
            print('equal_type_name: ', equal_type_name)
            print('ratio: ', best_ratio, ' more complete: ', more_complete, 'section: ', k, '-------->\n', diff, '\n')

        else:
            print("No similar section found in the second document.\n")

rdf_dict.keys()
rdf_dict['namespaces'] = {uri.split(':')[0]:"".join(uri.split(':')[1:]) for uri in rdf_dict['namespaces']}
rdf_dict['rdf_section'] = rdf_dict['namespaces']


for key in rdf_dict.keys():
    if key not in ['namespaces','rdf_section','doctype_section']:
        list_with_duplicates = rdf_dict[key]
        # list_with_duplicates is your original list
        list_without_duplicates = list(set(list_with_duplicates))
        rdf_dict[key] = list_without_duplicates
        print('###########################3')
        for item in rdf_dict[key]:
            print(item)

rdf_output = dict_to_rdf(rdf_dict)
print(rdf_output)
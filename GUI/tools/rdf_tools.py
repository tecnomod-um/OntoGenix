from lxml import etree
from rdflib import Graph, URIRef
import os


def get_subsections(namespaces, root, section_type):
    definitions = []
    for uri in namespaces.values():
        insert = '{uri}'.format(uri=uri)
        classes = [etree.tostring(e, pretty_print=True).decode() for e in root.findall('.//{' + insert + '}'+section_type)]
        for c in classes:
            definitions.append(c)
    return definitions


def extract_sections_from_rdf(rdf_string):
    # Convert string to bytes
    rdf_bytes = bytes(rdf_string, encoding='utf-8').strip(b'\n')
    # Parse RDF string to an XML object
    root = etree.fromstring(rdf_bytes)
    # Extract namespaces
    namespaces = root.nsmap
    # ---------------- Extract RDF section (uris definitions)
    # Extract class definitions
    class_definitions = get_subsections(namespaces, root, 'Class')
    # Extract object property definitions
    object_property_definitions = get_subsections(namespaces, root, 'Property')
    # Extract data property definitions
    data_property_definitions = get_subsections(namespaces, root, 'DatatypeProperty')

    rdf_sections = {
        'namespaces': namespaces,
        'class_definitions': class_definitions,
        'object_property_definitions': object_property_definitions,
        'data_property_definitions': data_property_definitions
    }

    return rdf_sections


def dict_to_rdf(rdf_sections):
    # Initialize root element
    root = etree.Element(
        '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF',
        rdf_sections['namespaces'],
        nsmap=rdf_sections['namespaces']
    )

    # Define namespaces
    namespaces = rdf_sections['namespaces']

    # Register namespaces
    for prefix, uri in namespaces.items():
        etree.register_namespace(prefix, uri)

    # Helper function to add children to root
    def add_children(items):
        for item in items:
            # Parse the XML string using the defined namespaces
            parser = etree.XMLParser(ns_clean=True, recover=True, remove_blank_text=True)
            child = etree.fromstring(item, parser=parser)
            root.append(child)

    # Add class definitions
    add_children(rdf_sections['class_definitions'])

    # Add object property definitions
    add_children(rdf_sections['object_property_definitions'])

    # Add data property definitions
    add_children(rdf_sections['data_property_definitions'])

    # Convert root to string and prepend doctype
    rdf_string = f'{rdf_sections["namespaces"]}\n{etree.tostring(root, pretty_print=True).decode()}'

    return rdf_string


def split_rdf(input_file: str, output_folder: str, chunk_size: int = 10):
    g = Graph()
    g.parse(input_file, format="xml")

    subjects = list(set(g.subjects()))
    chunks = [subjects[x:x+chunk_size] for x in range(0, len(subjects), chunk_size)]

    for i, chunk in enumerate(chunks, 1):
        chunk_g = Graph()
        for subject in chunk:
            for p, o in g.predicate_objects(URIRef(subject)):
                chunk_g.add((URIRef(subject), p, o))
        chunk_file = os.path.join(output_folder, f'chunk_{i}.rdf')
        chunk_g.serialize(destination=chunk_file, format='xml')

from owlready2 import *

ontology_path = './datasets/pizza.owl'
onto = get_ontology(ontology_path).load()
print(list(onto.classes()))
print(list(onto.object_properties()))
print(list(onto.data_properties()))

print(onto.metadata.comment)

for annot_prop in onto.metadata:
    print(annot_prop, ":", annot_prop[onto.metadata])



# Access a class in the ontology, e.g., Margherita pizza
class Pizza(Thing):
    namespace = onto

# Perform reasoning and classification
sync_reasoner()

# Print the instances of Margherita found in the ontology
for margherita in list(onto.search(type=Pizza)):
    print(margherita)

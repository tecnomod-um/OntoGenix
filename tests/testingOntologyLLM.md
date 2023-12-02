# Generation of mappings with OntoGenix

## Elements to compare

| Dataset | Human generated ontology | LLM generated ontology |
| ------- | ----------------------- | --------------------- |
| [BigBasketProducts](https://www.kaggle.com/datasets/chinmayshanbhag/big-basket-products) | [BigBasketProducts_ontology_human.owl](ontologies/BigBasketProducts_ontology_human.owl) | [BigBasketProducts_ontology_LLM.owl](ontologies/BigBasketProducts_ontology_LLM.owl) |
| [Brazilian e-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | [ontologies/BrazilianEcommerce_ontology_human.owl](ontologies/BrazilianEcommerce_ontology_human.owl) | [ontologies/BrazilianEcommerce_ontology_LLM.owl](ontologies/BrazilianEcommerce_ontology_LLM.owl) |
| [eCommerce](https://www.kaggle.com/datasets/carrie1/ecommerce-data) | [eCommerce_ontology_human.owl](ontologies/eCommerce_ontology_human.owl) | [eCommerce_ontology_LLM.owl](ontologies/eCommerce_ontology_LLM.owl) |
| [Airline customer satisfaction](https://www.kaggle.com/datasets/sjleshrac/airlines-customer-satisfaction) | [AirlinesCustomerSatisfaction_ontology_human.owl](ontologies/AirlinesCustomerSatisfaction_ontology_human.owl) | [AirlinesCustomerSatisfaction_ontology_LLM.owl](ontologies/AirlinesCustomerSatisfaction_ontology_LLM.owl) |
| [Amazon rating](https://www.kaggle.com/datasets/skillsmuggler/amazon-ratings) | [AmazonRatings_ontology_human.owl](ontologies/AmazonRatings_ontology_human.owl) | [AmazonRatings_ontology_LLM.owl](ontologies/AmazonRatings_ontology_LLM.owl) |
| [Customer complaints](https://www.kaggle.com/datasets/utkarshx27/consumer-complaint) | [CustomerComplaint_ontology_human.owl](ontologies/CustomerComplaint_ontology_human.owl) | [CustomerComplaints_ontology_LLM.owl](ontologies/CustomerComplaints_ontology_LLM.owl) |

## Results

### BigBasketProducts

* **Annotations:** The human generated ontology includes rdfs:label annotations for classes and properties, making the ontology more understandable to human users.

* **Classes:** Both ontologies have exactly the same classes, but the human-generated ontology includes more complex axioms in the restricions.

* **Object Properties:** The LLM-generated ontology presents more object properties, but the additional object properties should be modelled as data properties. In terms of axiomatic complexity in object properties, both ontologies are similar, with axioms for inverse object properties, domains and ranges.

* **Data Properties:** Data properties are similar in both ontologies, but human-generated ontologies present more properties from external ontologies, like schema.org

 Both ontologies present a similar coverage of the CSV data, but the human-generated ontology presents oportunities for a more detailed modelling.

### BrazilianEcommerce

* **Annotations:** The human generated ontology includes rdfs:label annotations for classes and properties, making the ontology more understandable to human users.

* **Classes:** Both ontologies have exactly the same classes, but the human-generated ontology includes more complex axioms in the restricions.

* **Object Properties:** Both ontologies present the same object properties and similar domain/range axioms. However, the LLM-generated ontology includes a useless axiom, namely `range owl:Thing`. The human generated ontology includes annotations in the object properties.

* **Data Properties:** Both ontologies present the same object properties. However, the LLM-generated repeats a property both as data property and object property.

### eCommerce

* **Annotations:** The human generated ontology includes rdfs:label annotations for classes and properties, making the ontology more understandable to human users.

* **Classes:** Both ontologies have exactly the same classes, but the human-generated ontology includes more complex axioms in the restricions.

* **Object Properties:** Both ontologies present similar object properties.

* **Data Properties:** The human generated ontology presents more data properties, related to the modelling presented in the classes hierarchy.

### AirlinesCustomerSatisfaction

* **Annotations:**

* **Classes:**

* **Object Properties:**

* **Data Properties:**

### AmazonRating

* **Annotations:** The human generated ontology includes rdfs:label annotations for classes and properties, making the ontology more understandable to human users.

* **Classes:** Both ontologies have the same number of classes (3) and the same class names, indicating a similar high-level conceptualization of the domain.

* **Object Properties:** Both ontologies define the same object properties (hasProduct and hasCustomer), suggesting a similar approach to modeling relationships between entities.

* **Data Properties:** This is a significant difference between the two ontologies. The LLM-generated ontology includes data properties that are unnecessary and redundant, like ProductId. Additionally, the DataType ranges are correctly assigned by the human (xsd:string, xsd:double and xsd:int) but the LLM only assignes xsd:string ranges

### CustomerComplaints

* **Annotations:**

* **Classes:**

* **Object Properties:**

* **Data Properties:**

## Conclusions

In general terms, human generated ontologies include 

more complex axioms in classes

more human-friendly annotations

a deeper coveraghe of CSV data

more complex axioms in object properties

In general humans entities of external ontologies (e.g. schema), being more interoperable.

Hallucinations: 

repeated properties as both data and obkect properties 
useless axiom, namely `range owl:Thing`


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

### BrazilianEcommerce

### eCommerce

### AirlinesCustomerSatisfaction

### AmazonRating

* **Annotations:** The human generated ontology includes rdfs:label annotations for classes and properties, making the ontology more understandable to human users.

* **Classes:** Both ontologies have the same number of classes (3) and the same class names, indicating a similar high-level conceptualization of the domain.

* **Object Properties:** Both ontologies define the same object properties (hasProduct and hasCustomer), suggesting a similar approach to modeling relationships between entities.

* **Data Properties:** This is a significant difference between the two ontologies. The LLM-generated ontology includes data properties that are unnecessary and redundant, like ProductId. Additionally, the DataType ranges are correctly assigned by the human (xsd:string, xsd:double and xsd:int) but the LLM only assignes xsd:string ranges

* **Relevance to the CSV Data:** The human-generated ontology has a clear advantage in terms of relevance to the CSV data. It includes data properties that directly correspond to the columns in the CSV file, such as timestamp and has_rating_value. The LLM-generated ontology, while structurally similar in terms of classes and object properties, lacks data properties that would represent the detailed attributes of the entities (like ratings and timestamps) found in the CSV data.

In conclusion, while both ontologies have a similar structure in terms of classes and object properties, the human-generated ontology is more comprehensive and relevant to the CSV data due to its inclusion of specific data properties that align with the data attributes. This makes the human-generated ontology more suited for applications that require detailed representation and analysis of the data contained in the CSV file.

### CustomerComplaints

## Conclusions


# Experiment with OntoGenix

## The datasets

We have evaluated OntoGenix by applying it to a series of Kaggle datasets related to commercial activities of organizations, which are described next:
* [Airlines Customer satisfaction](https://www.kaggle.com/datasets/sjleshrac/airlines-customer-satisfaction): customers who have already flown with them, including the feedback of the customers on various contexts
* [Amazon Ratings](https://www.kaggle.com/datasets/skillsmuggler/amazon-ratings): Customer reviews and ratings of Beauty related products sold on their website.
* [BigBasket Products](https://www.kaggle.com/datasets/chinmayshanbhag/big-basket-products): Products listed on the website of online grocery store Big Basket
* [Brazilian e-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): Brazilian e-commerce public dataset of orders made at Olist Store.
* [Customer complaint](https://www.kaggle.com/datasets/utkarshx27/consumer-complaint): Collection of complaints about consumer financial products
* [E-commerce](https://www.kaggle.com/datasets/carrie1/ecommerce-data): Transactions for a UK-based and registered non-store online retail.

The experiment has consisted on the development of ontologies with OntoGenix and their comparison with ontologies developed by humans.


## The LLM and the human ontologies 

The next table links the ontologies used in the evaluation. 

| Dataset | Human generated ontology | LLM generated ontology |
| ------- | ----------------------- | --------------------- |
| [BigBasketProducts](https://www.kaggle.com/datasets/chinmayshanbhag/big-basket-products) | [BigBasketProducts_ontology_human.owl](ontologies/BigBasketProducts_ontology_human.owl) | [BigBasketProducts_ontology_LLM.owl](ontologies/BigBasket_LLM.owl) |
| [Brazilian e-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | [BrazilianEcommerce_ontology_human.owl](ontologies/BrazilianEcommerce_ontology_human.owl) | [BrazilianEcommerce_ontology_LLM.owl](ontologies/Brazillian_LLM.owl) |
| [eCommerce](https://www.kaggle.com/datasets/carrie1/ecommerce-data) | [eCommerce_ontology_human.owl](ontologies/eCommerce_ontology_human.owl) | [eCommerce_ontology_LLM.owl](ontologies/Ecommerce_LLM.owl) |
| [Airline customer satisfaction](https://www.kaggle.com/datasets/sjleshrac/airlines-customer-satisfaction) | [AirlinesCustomerSatisfaction_ontology_human.owl](ontologies/AirlinesCustomerSatisfaction_ontology_human.owl) | [AirlinesCustomerSatisfaction_ontology_LLM.owl](ontologies/Airlines_LLM.owl) |
| [Amazon rating](https://www.kaggle.com/datasets/skillsmuggler/amazon-ratings) | [AmazonRatings_ontology_human.owl](ontologies/AmazonRatings_ontology_human.owl) | [AmazonRatings_ontology_LLM.owl](ontologies/Amazon_LLM.owl) |
| [Customer complaints](https://www.kaggle.com/datasets/utkarshx27/consumer-complaint) | [CustomerComplaint_ontology_human.owl](ontologies/CustomerComplaint_ontology_human.owl) | [CustomerComplaints_ontology_LLM.owl](ontologies/CustomerComplaint_LLM.owl) |

## Evaluation method

The evaluation has consisted in both a qualitative and a quantitative comparative assessment of the human and LLM ontologies.  The qualitative assessment was done by an ontology engineer. The quantitative assessment has been done by calculating and comparing the values of the 19 quality metrics included in the OQuaRE ontology evaluation framework. OQuaRE scales the values of the metrics to a Likert scale 1 (lowest score) to 5 (highest score). 

The LLM ontologies are in RDF/XML format despite OntoGenix generates them in Turtle. The files have been transformed into RDF/XML using the [EasyRDF Converter](https://www.easyrdf.org/converter). The reason for this conversion is that OQuaRE input ontologies must be in this format. 

In order to generate the OQuaRE scores we have used the [GitHub action available for OQuaRE](https://github.com/tecnomod-um/oquare-metrics), whose results are available in the [oquare folder](./oquare/). In the path oquare/results/ontologies there is one folder per ontology. For each ontology there is one *README.md* file which shows all the figures available in the *img* folder. OQuaRE outputs the values of the metrics in an XML file which is also provided in the *metrics* folder.


## Results of the Qualitative Evaluation

### BigBasketProducts

* **Annotations:** The LLM ontology contains more annotations than the human one, including labels in multiple languages, descriptions and comments.

* **Classes:** The LLM ontology has more classes. The LLM includes many equivalentClass axioms, which do not seem correct in some cases. For example "Has offer" is proposed as a class and as an object property with the same URI. The axioms in the human-generated ontology make more sense.

* **Object Properties:** The LLM-generated ontology presents more object properties, but some should not be modelled as  object properties, such as category or subcategory, which should be classes and other properties could have been created. In terms of axiomatic complexity in object properties, both ontologies are similar, with better axioms for inverse object properties, domains and ranges in the human ontologies.

* **Data Properties:** The LLM proposes more datatype properties and creates subhierarchies. The LLM proposes equivalencies between datatype properties, which are sometimes wrong (discounted price and price specification). Both are able to reuse properties from external ontologies, like schema.org. 


 Both ontologies present a similar coverage of the CSV data, but the human-generated ontology presents oportunities for a more detailed modelling.

### BrazilianEcommerce

* **Annotations:** The LLM ontology contains more annotations than the human one, including labels in multiple languages, descriptions and comments.

* **Classes:** The human ontology has more classes. The LLM includes many equivalentClass axioms, which do not seem correct in some cases, for example customer is not equivalent to Person. The LLM misses classes such as seller.

* **Object Properties:** The human ontology present the more object properties, but the domain/range axioms of the LLM are more precise.

* **Data Properties:** The human ontology present more datatype properties, underrepresenting the content of the CSV.

### eCommerce

* **Annotations:**  The LLM ontology contains more annotations than the human one, including labels in multiple languages, descriptions and comments.

* **Classes:** The number of classes are similar. The LLM ontology tend to create equivalent classes to schema classes, but those are not always right (such as consumer and customer) ontologies have exactly the same classes. The human ontology includes more complex and complete axioms in the restricions. The LLM does not generate the individuals generated by the human.

* **Object Properties:** Both ontologies present similar object properties.

* **Data Properties:** The human generated ontology presents more data properties, related to the modelling presented in the classes hierarchy.

### AirlinesCustomerSatisfaction

* **Annotations:** The LLM ontology contains more annotations than the human one, including labels in multiple languages, descriptions and comments.

* **Classes:** The human-generated ontology models some of the entities as individuals rather than classes, and it includes more entities, with a finer modelling, in doing so.

* **Object Properties:** Both ontologies present the same object properties, with identical domain/range. The LLM includes disjointess axioms.

* **Data Properties:** Both ontologies present similar data properties, with identical domain/range.

### AmazonRatings

* **Annotations:** The LLM ontology contains more annotations than the human one, including labels in multiple languages, descriptions and comments.

* **Classes:** Both ontologies have the same number of relevant classes  and the same class names, indicating a similar high-level conceptualization of the domain. However, the LLM adds some other classes, named ErrorX, which are an artifact of the process.

* **Object Properties:** Both ontologies define the same object properties (hasProduct and hasCustomer), suggesting a similar approach to modeling relationships between entities.

* **Data Properties:** This is a significant difference between the two ontologies. The LLM-generated ontology includes data properties that are unnecessary and redundant, like ProductId. Additionally, the DataType ranges are correctly assigned by the human (xsd:string, xsd:double and xsd:int) but the LLM only assignes xsd:string ranges

### CustomerComplaints

* **Annotations:** The LLM ontology contains more annotations than the human one, including labels in multiple languages, descriptions and comments. In some cases, the LLM does not provide annotatins.

* **Classes:** Both ontologies present the same useful classes, but the human-generated ontology presents further subsumption relationships between them. The LLM generates additional classes for establishing equivalencies, without practical usefulness.

* **Object Properties:** Both ontologies present similar object properties, but the human-generated ontology presents more domain/range axioms.

* **Data Properties:** Both ontologies present similar data properties, but the human-generated ontology presents more domain/range axioms.

### Conclusions of the qualitative evaluation

In general terms, human generated ontologies include:

* Axioms of higher expressivity in class restrictions and properties.
* More accurate linking with entities of external ontologies (e.g. schema), being more interoperable.
* A more nuanced understanding of OWL modelling: instances vs classes, when to add a subsumption relationship, the need for N-ary relationships, etc.

Additionally, in some cases, LLM-generated ontologies include hallucinations:

* Entities modelled as both data and object properties.
* Inappropriate equivalent relations.

The LLM ontologies are richer in annotations.

## Results of the Quantitative Evaluation

The next table shows for which metrics the LLM and the human ontologies got different scores for the metrics. A metric in a cell means which ontology got the higher score. We also show in the table who developed each ontology.

| Dataset | LLM ontology | Human  ontology | Ontologist |
| ------- | ----------------------- | --------------------- | ---------------------| 
| Airlines Customer satisfaction  | RFCOnto, NOMOnto | WMCOnto2, NOCOnto, DITOnto, LCOMOnto | A |
| Amazon Ratings  | RROnto, NOMOnto, INROnto | WMCOnto2, TMOnto2, TMOnto, PROnto, DITOnto, ANOnto | A|
| BigBasket Products  | ANOnto | NOCOnto | B|
| Brazilian e-commerce  | RROnto, RFCOnto, NOMOnto, NOCOnto, CROnto, AROnto | PROnto | B|
| Customer complaint  | NOCOnto,CROnto, AROnto, ANOnto | WMCOnto2, NOMOnto, DITOnto | A|
| E-commerce  | RROnto, RFCOnto, NOMOnto, NOCOnto, ANOnto | PROnto | B|


### Conclusions of the quantitative evaluation

* The LLM ontologies obtain higher scores for RFCOnto (related to the number of usages of object, datatype properties and superclasses), NOMOnto (related to the average number of properties per class), RROnto (related to the ratio of taxonomic relations and object properties)and ANOnto (related to the ratio of annotations).

* The human ontologies obtain higher scores for WMCOnto2 (related to the number of paths in the ontology), DITOnto (related to the depth of the hierarchy) and PROnto (related to the ratio of properties).

* The human ontologies developed by A tend to have more metrics with higher scores than the LLM, whereas the opposite happens for B.
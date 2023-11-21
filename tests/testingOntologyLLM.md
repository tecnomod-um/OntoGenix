# Generation of mappings with OntoGenix

## Elements to compare

| Dataset | Human generated ontology | LLM generated ontology |
| ------- | ----------------------- | --------------------- |
| [BigBasketProducts](https://www.kaggle.com/datasets/chinmayshanbhag/big-basket-products) | [mapping.csv.ttl](../../Transformation/BigBasketProductsCSV2RDF/Mappings/mapping.csv.ttl) | [mappingLLM.csv.ttl](../../Transformation/BigBasketProductsCSV2RDF/Mappings/mappingLLM.csv.ttl) |
| [Walmart products](https://data.world/promptcloud/walmart-product-data-from-usa) | [mapping.csv.ttl](../../Transformation/WalmartProductDetails/Mappings/mapping.csv.ttl) | [mappingLLM.csv.ttl](../../Transformation/WalmartProductDetails/Mappings/mappingLLM.csv.ttl) |
| [Brazilian e-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | [mapping_customers.ttl](../../Transformation/BrazilianE-commerceCSV2RDF/Mappings/mapping_customers.ttl), [mapping_geolocation.ttl](../../Transformation/BrazilianE-commerceCSV2RDF/Mappings/mapping_geolocation.ttl), [mapping_order_items.ttl](../../Transformation/BrazilianE-commerceCSV2RDF/Mappings/mapping_order_items.ttl), [mapping_order_payments.ttl](../../Transformation/BrazilianE-commerceCSV2RDF/Mappings/mapping_order_payments.ttl), [mapping_order_reviews.ttl](../../Transformation/BrazilianE-commerceCSV2RDF/Mappings/mapping_order_reviews.ttl), [mapping_orders.ttl](../../Transformation/BrazilianE-commerceCSV2RDF/Mappings/mapping_orders.ttl), [mapping_products.ttl](../../Transformation/BrazilianE-commerceCSV2RDF/Mappings/mapping_products.ttl), [mapping_sellers.ttl](../../Transformation/BrazilianE-commerceCSV2RDF/Mappings/mapping_sellers.ttl), | [mappingLLM.csv.ttl](../../Transformation/BrazilianE-commerceCSV2RDF/Mappings/mappingLLM.csv.ttl) |
| [eCommerce](https://www.kaggle.com/datasets/carrie1/ecommerce-data) | [mapping.csv.ttl](../../Transformation/eCommerceCSV2RDF/Mappings/mapping.csv.ttl) | [mappingLLM.csv.ttl](../../Transformation/eCommerceCSV2RDF/Mappings/mappingLLM.csv.ttl) |
| [Airline customer satisfaction](https://www.kaggle.com/datasets/sjleshrac/airlines-customer-satisfaction) | [mapping.csv.ttl](../../Transformation/AirlinesCustomerSatisfactionCSV2RDF/Mappings/mapping.csv.ttl) | [mappingLLM.csv.ttl](../../Transformation/AirlinesCustomerSatisfactionCSV2RDF/Mappings/mappingLLM.csv.ttl) |
| [Amazon rating](https://www.kaggle.com/datasets/skillsmuggler/amazon-ratings) | [mapping.csv.ttl](../../Transformation/AmazonRatingCSV2RDF/Mappings/mapping.csv.ttl) | [mappingLLM.csv.ttl](../../Transformation/AmazonRatingCSV2RDF/Mappings/mappingLLM.csv.ttl) |
| [Customer complaints](https://www.kaggle.com/datasets/utkarshx27/consumer-complaint) | [mapping.csv.ttl](../../Transformation/CustomerComplaintCSV2RDF/Mappings/mapping.csv.ttl) | [mappingLLM.csv.ttl](../../Transformation/CustomerComplaintCSV2RDF/Mappings/mappingLLM.csv.ttl) |

## Results

### BigBasketProducts



### AirlinesCustomerSatisfaction



### AmazonRating

* **Classes:** Both ontologies have the same number of classes (3) and the same class names, indicating a similar high-level conceptualization of the domain.

* **Object Properties:** Both ontologies define the same object properties (hasProduct and hasCustomer), suggesting a similar approach to modeling relationships between entities.

* **Data Properties:** This is a significant difference between the two ontologies. The human-generated ontology includes 4 data properties, which are likely used to represent attributes of the entities such as ratings and timestamps. This aspect is missing in the LLM-generated ontology.

* **Relevance to the CSV Data:** The human-generated ontology has a clear advantage in terms of relevance to the CSV data. It includes data properties that directly correspond to the columns in the CSV file, such as timestamp and has_rating_value. The LLM-generated ontology, while structurally similar in terms of classes and object properties, lacks data properties that would represent the detailed attributes of the entities (like ratings and timestamps) found in the CSV data.

In conclusion, while both ontologies have a similar structure in terms of classes and object properties, the human-generated ontology is more comprehensive and relevant to the CSV data due to its inclusion of specific data properties that align with the data attributes. This makes the human-generated ontology more suited for applications that require detailed representation and analysis of the data contained in the CSV file.


### BrazilianEcommerce



### CustomerComplaints



### eCommerce



### WalmartProductDetails



## Conclusions


# Generation of mappings by large language models

The experiments consist on asking an LLM to generate the mappings combining the previous two subtasks. The main goal of these experiments is to learn if LLMs can help and how, what kind of interaction processes and contextual information can be defined.

## Testing software

The asessment of the mappings have been manually done, although [software](../software/software-LLM.md) has been used for generating the mappings.

## Description of the experiment

Elements to compare:

| Dataset | Human generated mapping | LLM generated mapping |
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

* **Coverage**: LLM misses one column, `Absolute_Url`.
* **URI templates for resources**:
  * LLM generates URI templates that are exactly the same as the vocabulary used to annotate the data, e.g. `https://vocab.um.es#product{ProductName}` rather than `https://data.um.es/bigbasketproduct/{ProductName}` (They are also based on the URI fragment, rather than using slashes all the way, and the lack readability since they paste directly the product name into the URI).
  * The LLM generates URI templates that do not warrant uniqueness of the resource, since `ProductName` is repeated in various lines of the CSV.
* **Type assignment**: LLM assigns types of the local ontology only, no external types are assigned, like `schema:Product`.
* **Property assignment**: LLM assigns only properties of the local ontology, e.g. `schema:price` is not assigned.
* **Datatype assignment**: LLM makes the following mistakes:
  * No datatype assigned (e.g. `rml:reference "Brand"` needs a `xsd:string` or `@en` tag).
  * Wrong datatype assigned (e.g. `rml:reference "Image_Url"` should be a `xsd:anyURI` instead of a `xsd:string`).
* **Literal/object assignment**: 
  * LLMs generates objects for `Category` and `Subcategory` values, which might be a good modelling decision, but in this case is not recommended since the category/subcategory combination pertains to each resource, and therefore that relation is lost (all the categories with the same name are collapsed into a single URI).
  * The generated category/subcategory objects are not connected to the products in any way, making them useless. 

### AirlinesCustomerSatisfaction

* **Coverage**: LLM covers all columns.
* **URI templates for resources**: LLM generates URI templates that are exactly the same as the vocabulary used to annotate the data, e.g. `https://vocab.um.es/customer/{customer_id}` rather than `https://data.um.es/customer_feedback/{customer_id}`.
* **Type assignment**: 
* **Property assignment**: 
* **Datatype assignment**: 
* **Literal/object assignment**: 

### AmazonRating

* **Coverage**: LLM covers all columns.
* **URI templates for resources**: 
  * LLM generates URI templates that are exactly the same as the vocabulary used to annotate the data, e.g. `https://vocab.um.es#User_{UserId}` rather than `https://data.um.es/amazon_ratings/user/{UserId}` (They are also based on the URI fragment, rather than using slashes all the way).
  * The LLM generates URI templates that do not warrant uniqueness of the resource, like `https://data.um.es/amazon_ratings/rating/{UserId}-{ProductId}-{Rating}-{Timestamp}` (The same user can rate teh same product with a different rating in a different date).
* **Type assignment**: LLM assigns types of the local ontology only, no external types are assigned, like `schema:Rating`.
* **Property assignment**: LLM assigns only properties of the local ontology, but the human made mapping also.
* **Datatype assignment**: LLM assigns no datatypes, but the human made mapping either, so there is no difference.
* **Literal/object assignment**: LLM defines objects for timestamps and ratings, which are modelled as literals by the human.

### BrazilianEcommerce

**Note**: only mappings pertaining to customers are compared.

* **Coverage**: LLM covers all columns.
* **URI templates for resources**:
  * LLM generates URI templates that are exactly the same as the vocabulary used to annotate the data, e.g. `http://example.com/ontology#customer{customer_id}` rather than `https://data.um.es/brazilian_ecommerce/customer/{customer_unique_id}` (They are also based on the URI fragment, rather than using slashes all the way).
* **Type assignment**: LLM assigns types of the local ontology only, no external types are assigned, but the human made mapping does the same.
* **Property assignment**: LLM assigns only properties of the local ontology, but the human made mapping also.
* **Datatype assignment**: LLM assigns no datatypes, but the human made mapping either, so there is no difference.
* **Literal/object assignment**: human generated mapping creates more complex relations to intermediate resources, using data from other files.

### CustomerComplaints

* **Coverage**: LLM generated mapping misses columns `Complaint ID`, `Company public response`
* **URI templates for resources**:
  * LLM generates URI templates that are exactly the same as the vocabulary used to annotate the data, e.g. `https://vocab.um.es#ComplaintID/{Complaint ID}` rather than `https://data.um.es/customer_complaints/complaint/{Complaint ID}`.
  * LLM generates URI templates that are based on the URI fragment, rather than using slashes all the way, and insert a slash after the fragment, making the fragment useless: `https://vocab.um.es#Product/{Complaint ID}`.
  * LLM generates URI templates that add names of other classes (`Product`), making the URI uninformative: `https://vocab.um.es#Product/{Complaint ID}`.
* **Type assignment**: LLM assigns types of the local ontology only, no external types are assigned, but the human made mapping does the same.
* **Property assignment**: LLM assigns only properties of the local ontology (The human added `rdfs:label`).
* **Datatype assignment**: LLM assigns no datatypes (The human assigned `xsd:date`).
* **Literal/object assignment**: human generated mapping creates more complex relations to intermediate resources, using data from other files.

### eCommerce

* **Coverage**: LLM covers all columns.
* **URI templates for resources**:
  * LLM generates URI templates that are exactly the same as the vocabulary used to annotate the data, e.g. `https://vocab.um.es#Invoice/{InvoiceNo}` rather than `https://data.um.es/{InvoiceNo}`.
  * LLM generates URI templates that are based on the URI fragment, rather than using slashes all the way, and insert a slash after the fragment, making the fragment useless: `https://data.um.es/{InvoiceNo}`.
  * Human generates templates that warrantee uniqueness, like `https://data.um.es/{InvoiceNo}_{StockCode}_{UnitPrice}`.
* **Type assignment**: LLM assigns types of the local ontology only, no external types are assigned, like `schema:Product`.
* **Property assignment**: LLM assigns only properties of the local ontology, e.g. `schema:priceCurrency` is not assigned.
* **Datatype assignment**: LLM assigns no datatypes (The human assigned `xsd:double`).
* **Literal/object assignment**: human generates more complex structures, like the one relating Sales Articles to Unit Price Specifications, which are further extended.

### WalmartProductDetails

* **Coverage**: LLM misses columns `Crawl Timestamp`, `Product Url`, `Item Number`, `Postal Code`.
* **URI templates for resources**:  LLM generates URI templates that are exactly the same as the vocabulary used to annotate the data, e.g. `https://vocab.um.es#Product{Uniq Id}` rather than `https://data.um.es/salesarticle/{Uniq Id}` (They are also based on the URI fragment, rather than using slashes all the way).
* **Type assignment**: LLM assigns types of the local ontology only, no external types are assigned, like `schema:Product`.
* **Property assignment**: LLM assigns only properties of the local ontology, e.g. `schema:brand` is not assigned.
* **Datatype assignment**: LLM assigns no datatypes (The human assigned `xsd:double`, `xsd:anyUri`).
* **Literal/object assignment**: human generates more complex structures, like the one relating Sales Articles to Products.

## Conclusions

LLMs can be very helpful in the mechanics of the mapping generation, i.e. in the generation of a first, rough mapping in a file. Such mapping should be considerably refined by a human paying attention to:

* Coverage (Sometimes LLM misses a column or two from the original data).
* URI templates:
  * Correctness (e.g. no ontology URI, no fragment, ...).
  * Uniqueness warrantee. Sometimes values from different columns need to be combined to generate unique URIs, or even generate UUIDs.
* Type assignment from other ontologies.
* Resource/literal assignment.
* Complex resource relations, e.g. `x has_product y`, `y has_price z`, `z has_currency x`.
* Datatype assignment:
  * No datatypes assigned.
  * PArsing of values to generate proper datatypes.

# Test datasets

## About

List of possible datasets to test the state of the art. The datasets were selected taking into account the [ontology](../Ontology/version2.2.drawio), so a (non-exhaustive) list of ontology terms found in the dataset (i.e. column names) are included.

## Datasets

### BigBasket products

* URL: https://www.kaggle.com/datasets/chinmayshanbhag/big-basket-products
* Format: CSV
* Ontology terms: ProductName (PRDName), Brand (BrandName)

### Walmart product data from USA

* URL: https://data.world/promptcloud/walmart-product-data-from-usa
* Format: CSV
* Ontology terms: product_name (PRDName), item_number (articleNumber), gtin (GTIN_EAN)

### Brazilian E-Commerce Public Dataset by Olist

* URL: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
* Format: CSV
* Ontology terms: customer_id (companyCode), customer_state (Country)

### E-Commerce Data

* URL: https://www.kaggle.com/datasets/carrie1/ecommerce-data
* Format: CSV
* Ontology terms: InvoiceNo (salesDocumentNo), StockCode (GTIN_EAN), Description (description), Quantity (complaintQuantity), InvoiceData (dateFirstGoodsReceived), CustomerID (companyCode), Country (Country)

### Airlines Customer satisfaction

* URL: https://www.kaggle.com/datasets/sjleshrac/airlines-customer-satisfaction
* Format: CSV
* Ontology terms: without alignment

### Amazon - Ratings

* URL: https://www.kaggle.com/datasets/skillsmuggler/amazon-ratings
* Format: CSV
* Ontology terms: ASIN (articleNumber?), Rating (value)

### Consumer Complaint Database

* URL: https://www.kaggle.com/datasets/utkarshx27/consumer-complaint
* Format: CSV
* Ontology terms: Data_received (dateNotificationCreated), Product (productName), Issue (ProblemOfComplaint), Customer_complaint_narrative (ProblemSubCategory), Company (Company), State (Country)

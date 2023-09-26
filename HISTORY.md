# Design evolution

![GitHub Logo](/images/OntoGenix_0.1.0.png)

1-Direct transformation of csv data to a RDF/XML ontology and RML mapp.<br/>
2-Lack of contextual information for LLM’s generates very basic ontologies in terms of semantics and interoperability. <br/>
3-Extensive use of www.example.com uri as foundational prefix. <br/>

![GitHub Logo](/images/OntoGenix_0.1.1.png)

![GitHub Logo](/images/OntoGenix_0.1.1_detail.png)

1-Three different LLM models in interaction: PlanSage, OntoBuilder and OntoMapper.<br/>
2-PlanSage: Human-in-the-loop paradigm to generate contextualized instructions. <br/>
3-OntoBuilder: Model-to-Model loop paradigm with PlanSage. <br/>
4-CSV’ data with contextualized instructions aligns better with user design objectives.<br/>
5-Still the generated ontologies are very basic in terms of semantics and interoperability.<br/>

![GitHub Logo](/images/OntoGenix_0.1.2.png)

![GitHub Logo](/images/OntoGenix_0.1.2_detail_a.png)

![GitHub Logo](/images/OntoGenix_0.1.2_detail_b.png)

1-The model is able to copy the semantic structure from the human generated examples and takes entities also for enrichment.<br/>
2-Due to the stochastic nature of the LLM model is hard to control or guide the outputs generated. <br/>
3-Models have contextual memory limitations so that completely rewriting the ontology causes loss of semantics previously achieved through model instruction.<br/>

![GitHub Logo](/images/OntoGenix_0.1.3.png)

![GitHub Logo](/images/OntoGenix_0.1.3_step_1.png)

![GitHub Logo](/images/OntoGenix_0.1.3_step_2.png)

![GitHub Logo](/images/OntoGenix_0.1.3_step_3.png)

1-Ontology segmentation drives to a better control of the stochastic nature of the LLM model. <br/>
2-The LLM focuses on specific content for each entity.<br/>
3-SemanticoAI enables better embedding space alignment.<br/>
4-The enrichment process is therefore better performed.<br/>

![GitHub Logo](/images/SemanticoAI_0.1.0.png)

1-LLM models have vast knowledge so they are able to understand acronyms, labels and descriptions of concepts from a wide range of knowledge.<br/>
2-This makes them useful to generate understandable descriptions for each entity that can be used to generate embeddings. <br/>
3-This saves most of the problems that are generated when trying to generate embeddings directly from entity properties, either by NLP methods or by graph embeddings.<br/>
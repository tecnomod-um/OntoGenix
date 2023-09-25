# OntoGenix

The project utilizes the OpenAI GPT-4 model to develop a semi-automatic system that generates OWL ontologies and RML mappings from CSV datasets using LLMs.

## Architecture

![GitHub Logo](/images/OntoGenix_0.1.3.png)

## Installation

```bash
pip install -r requirements.txt
```

## Execution

The pipeline is configured in a YAML file called `config.yaml` with only one section called `OntoGenixConfig`:

```yaml
OntoGenixConfig:
    base_path : "./datasets/"
    dataset_folder : "CustomerComplaint"
    dataset_file : "complaints"
```

The program always expects a main folder (`base_path`). Each dataset should have its own subfolder (`dataset_folder`) containing a CSV file `dataset_file`, and the CSV file name in the configuration should not have the `.csv` suffix (The actual file name should have the suffix though).

The Open AI ChatGPT API key should be provided in an environment variable:

```bash
export OPENAI_API_KEY=...
```

To execute the pipeline:

```bash
python3 pipeline.py
```

## Pipeline Description
### Summary:

This code represents a comprehensive pipeline that transforms a dataset into a knowledge graph, with intermediate steps involving ontology generation and mapping creation. Below is a high-level summary of each step in this pipeline:

1. **Configuration Loading:**
   - It starts by loading the configuration parameters from a YAML file named `config.yaml`, which includes parameters such as base_path, dataset_folder, and dataset_file.
   
2. **CSV Chunking:**
   - A subsample of a CSV dataset is extracted and displayed, with a maximum token limit set to 200 per row.

3. **Dataframe to JSON Conversion:**
   - This subsample is then transformed to a JSON format and saved into a file.

4. **JSON to CSV Conversion:**
   - The JSON data is then read and converted back to a new CSV file.

5. **MORPHKG Configuration:**
   - A configuration INI file for MORPHKG is generated, containing mappings and file_path pointing to the newly created CSV file.

6. **Plan Instructions Generation:**
   - Utilizing a planner from `PlanSage.LLM_planner`, high-level structure of the ontology is defined in natural language, based on the instruction, metadata, and the dataset.

7. **Ontology Generation:**
   - The `LlmOntology` class from `OntoBuilder.LLM_ontology` is used to build a base ontology based on high-level definitions, and it can also generate code blocks for specific entities within the ontology.
   - Different prompts are utilized for improving class entities and object/data properties, ensuring comprehensive and flexible understanding and usage of each entity in the ontology.

8. **RML Mapping Generation:**
   - The `LlmOntoMapper` from `OntoMapper.LLM_ontomapper` is then used to create RML mappings between the ontology and the source data based on the contextual information from the ontology.
   
9. **Knowledge Graph Materialization:**
   - Finally, using the `morph_kgc.materialize` method, the knowledge graph is generated from the RML code and is serialized into ‘ntriples’ format, creating a `.nt` file.

### Notable Details:
- There are provisions to regenerate the answers from the LLM models at different stages if required.
- The ontology building step has extensive functionalities to refine, define constraints, relationships, and metadata for every entity involved.
- The pipeline leverages configurations for different stages, making it modular and adaptable to different datasets and requirements.
- There are placeholders for future refinements and enhancements such as exploring OpenAI embeddings and refining the Mapper strategy.
- Several TODOs and IDEAS are noted in the comments for future refinements, enhancements, and strategies to improve ontology building and knowledge graph generation.

This is a versatile and comprehensive pipeline, reflecting a systematic approach to transforming structured data into a semantically rich knowledge graph, with intermediate ontology engineering and mapping steps, allowing for extensive customization and refinement.

## Design evolution

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


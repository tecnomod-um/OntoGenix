# OntoGenix

A semi-automatic systems to generate OWL ontologies from CSV datasets using LLMs.

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

## Design evolution

![GitHub Logo](/images/OntoGenix_0.1.0.png)

1-Direct transformation of csv data to a RDF/XML ontology and RML mapp.<br/>
2-Lack of contextual information for LLM’s generates very basic ontologies in terms of semantics and interoperability. <br/>
3-Extensive use of www.example.com uri as foundational prefix. <br/>

![GitHub Logo](/images/OntoGenix_0.1.1.png)

![GitHub Logo](/images/OntoGenix_0.1.1_detail.png)

1-Three different LLM models in interaction: PlanSage, OntoBuilder and OntoMapper.
2-PlanSage: Human-in-the-loop paradigm to generate contextualized instructions. 
3-OntoBuilder: Model-to-Model loop paradigm with PlanSage. 
4-CSV’ data with contextualized instructions aligns better with user design objectives.
5-Still the generated ontologies are very basic in terms of semantics and interoperability.

![GitHub Logo](/images/OntoGenix_0.1.2.png)

![GitHub Logo](/images/OntoGenix_0.1.2_detail_a.png)

![GitHub Logo](/images/OntoGenix_0.1.2_detail_b.png)

1-The model is able to copy the semantic structure from the human generated examples and takes entities also for enrichment.
2-Due to the stochastic nature of the LLM model is hard to control or guide the outputs generated. 
3-Models have contextual memory limitations so that completely rewriting the ontology causes loss of semantics previously achieved through model instruction.

![GitHub Logo](/images/OntoGenix_0.1.3.png)

![GitHub Logo](/images/OntoGenix_0.1.3_step_1.png)

![GitHub Logo](/images/OntoGenix_0.1.3_step_2.png)

![GitHub Logo](/images/OntoGenix_0.1.3_step_3.png)

1-Ontology segmentation drives to a better control of the stochastic nature of the LLM model. 
2-The LLM focuses on specific content for each entity.
3-SemanticoAI enables better embedding space alignment.
4-The enrichment process is therefore better performed.

![GitHub Logo](/images/SemanticoAI_0.1.0.png)

1-LLM models have vast knowledge so they are able to understand acronyms, labels and descriptions of concepts from a wide range of knowledge.
2-This makes them useful to generate understandable descriptions for each entity that can be used to generate embeddings. 
3-This saves most of the problems that are generated when trying to generate embeddings directly from entity properties, either by NLP methods or by graph embeddings.


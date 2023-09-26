# OntoGenix

The OntoGenix Python pipeline is able to build [OWL](https://www.w3.org/TR/owl2-overview/) ontologies and [RML](https://rml.io/specs/rml/) mappings from CSV datasets semi-automatically. In order to do so, it uses the [OpenAI GPT-4 model](https://platform.openai.com/docs/models/gpt-4) through its API.

## Architecture

![OntoGenix 0.1.3](/images/OntoGenix_0.1.3.png)

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

### Summary

This code represents a comprehensive pipeline that transforms a dataset into a Knowledge Graph, with intermediate steps involving ontology generation and mapping creation. Below is a high-level summary of each step in this pipeline:

1. **Configuration Loading**: It starts by loading the configuration parameters from a YAML file named `config.yaml`, which includes parameters such as `base_path`, `dataset_folder`, and `dataset_file`.
   
2. **CSV Chunking:** A subsample of a CSV dataset is extracted and displayed, with a maximum token limit set to 200 per row.

3. **Dataframe to JSON Conversion:** This subsample is then transformed to a JSON format and saved into a file.

4. **JSON to CSV Conversion:** The JSON data is then read and converted back to a new CSV file.

5. **Morph-KGC Configuration:** A configuration INI file for [Morph-KGC](https://morph-kgc.readthedocs.io/en/latest/) is generated, containing mappings and a `file_path`` pointing to the newly created CSV file.

6. **Plan Instructions Generation:** Using a planner from `PlanSage.LLM_planner`, a high-level structure of the ontology is defined in natural language, based on the instruction, metadata, and the dataset.

7. **Ontology Generation:**
   - The `LlmOntology` class from `OntoBuilder.LLM_ontology` is used to build a base ontology based on high-level definitions, and it can also generate code blocks for specific entities within the ontology.
   - Different prompts are utilized for improving class entities and object/data properties, ensuring comprehensive and flexible understanding and usage of each entity in the ontology.

8. **RML Mapping Generation:** The `LlmOntoMapper` from `OntoMapper.LLM_ontomapper` is then used to create RML mappings between the ontology and the source data based on the contextual information from the ontology.
   
9. **Knowledge Graph Materialization:** Finally, using the `morph_kgc.materialize` method, the Knowledge Graph is generated from the RML code and is serialized into NTriples format, creating a `.nt` file.

### Notable Details

- There are provisions to regenerate the answers from the LLM models at different stages if required.
- The ontology building step has extensive functionalities to refine, define constraints, relationships, and metadata for every entity involved.
- The pipeline leverages configurations for different stages, making it modular and adaptable to different datasets and requirements.
- There are placeholders for future refinements and enhancements such as exploring OpenAI embeddings and refining the Mapper strategy.
- Several [tasks and ideas are noted](https://github.com/mikelval82/OntoGenix/issues) for future refinements, enhancements, and strategies to improve ontology building and Knowledge Graph generation.

This is a versatile and comprehensive pipeline, reflecting a systematic approach to transforming structured data into a semantically rich Knowledge Graph, with intermediate ontology engineering and mapping steps, allowing for extensive customization and refinement.



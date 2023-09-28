# TODO List

## Tasks:
- **Generalize `extract_sections_from_rdf` Method:**
  - [x] The method in the tools package must be generalized for extracting classes using a set of different URIs.
  - [x] Add try-catch building blocks.
  
- **Review Prompts:**
  - [x] Revise every prompt on every agent.

- **Rewrite the Pipeline:**
  - [x] Make the generation of the ontology more straightforward.
  - [x] The RML must be done in two steps: first, generate the rationale and then the RML code.
  - [ ] Clarify the embeddings' strategy.


## PlanSage agent Integration Tasks:
  - [x] Include a set of tasks to force the model to use some specific URIs for classes, object properties, data properties, and annotations. These tasks are fixed, and the goal for PlanSage is to generate the short-term memory that will provide the appropriate context for the OntoBuilder to better understand the JSON data.

### Note:
The tasks listed are crucial for enhancing the model's ability to understand and interpret JSON data effectively by using specific URIs.





# OntoGenix

A semi-automatic systems to generate OWL ontologies from CSV datasets using LLMs.

## Architecture

![GitHub Logo](/images/OntoGenix_0.1.2.png)

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

To execute the pipeline:

```bash
python3 pipeline.py
```

import re
import matplotlib.pyplot as plt
from collections import Counter
from sentence_transformers import util
import numpy as np

def clean_word(word):
    cleaned = "".join([char.lower() for char in word if not char.isnumeric()])
    cleaned = re.sub('\(.*\)', '', cleaned)
    return cleaned


def process_semantic_descriptions(semantic_descriptions: dict, key: str = 'proposed_name') -> list:
    if key == 'proposed_name':
        return [clean_word(semantic_descriptions[key]['proposed_name']) for key in semantic_descriptions.keys()]
    elif key == 'description':
        return [semantic_descriptions[key]['description'] for key in semantic_descriptions.keys()]


def get_relevant_chunks(labels, all_labels, reference_semantic_descriptions, ontology_embeddings_2d):
    cosine_scores = util.cos_sim(ontology_embeddings_2d, ontology_embeddings_2d)
    print(cosine_scores.shape)

    pairs = []
    for i in range(len(cosine_scores) - 1):
        for j in range(i + 1, len(cosine_scores)):
            pairs.append({'index': [i, j], 'score': cosine_scores[i][j]})

    sorted_pairs = sorted(pairs, key=lambda x: x['score'].item(), reverse=True)

    entities = dict()
    for word2check in labels:
        word2check_index = all_labels.index(word2check)
        entities[word2check] = []
        cont = 0
        for pair in sorted_pairs:
            i, j = pair['index']
            if i == word2check_index and all_labels[i] != all_labels[j] and all_labels[j] not in entities[word2check]:
                print(all_labels[i], ' ', all_labels[j], ' ', pair['score'])

                entities[word2check].append({'entity': all_labels[j], 'i': i, 'j': j})
                cont += 1
            if cont == 3:
                break

    segment_files = []
    for key in entities.keys():
        for item in entities[key]:
            for it, ref_key in enumerate(reference_semantic_descriptions.keys()):
                if it == item['j'] - len(labels):
                    segment_files.append(reference_semantic_descriptions[ref_key]['file'])
                    break

    sorted_files = sorted(segment_files, key=lambda x: int(x.split('chunk_')[1].split('.')[0]))
    print(sorted_files)

    # Count the frequency of each string
    counter = Counter(sorted_files)

    # Separate keys and values for plotting
    labels, values = zip(*counter.items())
    values = np.array(values)

    # Create the histogram
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values)
    plt.xticks(rotation='vertical')
    plt.show()

    index = [it for it, val in enumerate(values) if val > values.mean() + values.std()]
    selected_chunks = [labels[it] for it in index]
    print(selected_chunks)
    return selected_chunks


def load_chunk_samples(files):
    examples = []
    # Iterate over the files and perform operations
    for file_path in files:
        # get the content from this file
        with open(file_path, 'r') as file:
            content = file.read()
        examples.append(content)
    return examples
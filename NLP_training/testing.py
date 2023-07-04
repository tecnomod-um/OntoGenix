import numpy as np
import yaml
'''########################################## YAML CONFIG ######################################################'''

with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded["OntoGenixConfig"]

base_path = config["base_path"]
dataset_folder = config["dataset_folder"]
dataset_file = config["dataset_file"]
def clean_word(word):
    cleaned = "".join([char for char in word if not char.isnumeric()])
    cleaned = cleaned.replace('_', ' ')
    cleaned = cleaned.lower()
    cleaned = cleaned.replace('(..*)', '')
    cleaned = cleaned.replace('.', '')
    return cleaned

chunks_folder = base_path + dataset_folder + '/chunks/'
dictionaries = np.load(chunks_folder + 'dictionaries.npy', allow_pickle=True).item()
labels = []
sentences = []
for label, sentence in dictionaries.items():
    if type(label) == str and type(sentence) == str:
        labels.append(clean_word(label))
        sentences.append(clean_word(sentence))
print(len(labels), len(sentences))

reference_folder = './datasets/GoodRelations_V1/chunked/'
reference_dictionaries = np.load(reference_folder + 'dictionaries.npy', allow_pickle=True).item()
reference_labels = []
reference_sentences = []
for label, sentence in reference_dictionaries.items():
    if type(label) == str and type(sentence) == str:
        reference_labels.append(clean_word(label))
        reference_sentences.append(clean_word(sentence))
print(len(reference_labels), len(reference_sentences))

final_labels = labels + reference_labels
final_sentences = sentences + reference_sentences
print(len(final_labels), len(final_sentences))

final_data = [label+': '+sentence for label,sentence in zip(final_labels, final_sentences)]


from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

nltk.download('stopwords')
nltk.download('punkt')

stop_words = set(stopwords.words('english'))
stop_words.add('')
stop_words.add('gr')

text = ''
for sentence in final_labels:
    text = text + sentence + ' '

word_tokens = word_tokenize(text)
filtered_text = [w for w in word_tokens if not w in stop_words]
print(filtered_text)

table = str.maketrans('', '', string.punctuation)
stripped = [w.translate(table) for w in filtered_text]
filtered_sentence = [w for w in stripped if not w in stop_words]
print(filtered_sentence)

import matplotlib.pyplot as plt
from collections import Counter

word_freq = Counter(filtered_sentence)
# Let's assume 'word_freq' is a dictionary with words as keys and their frequencies as values
words = list(word_freq.keys())
frequencies = list(word_freq.values())

index_freq = list(enumerate(frequencies))
sorted_list = sorted(index_freq, key=lambda x: x[1], reverse=True)
new_index = [it for it,_ in sorted_list]
words_indexed = [words[it] for it in new_index]
frequencies_indexed = [freq for it,freq in sorted_list]

plt.figure()
plt.bar(words_indexed, frequencies_indexed)
plt.show()

# Let's assume you have a list of words 'word_list'
wordcloud = WordCloud(width = 1000, height = 500).generate(' '.join(words_indexed))

plt.figure(figsize=(15,8))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()
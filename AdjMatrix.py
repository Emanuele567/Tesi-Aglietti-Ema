#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pyexcel_ods
import pandas as pd
import re
from collections import defaultdict
from IPython.display import display

# Carica il file ODS, prende il percorso e poi lo usa per l'assegnazione a "data"
file_path = "C:/Users/leloa/Desktop/dataset.ods"
data = pyexcel_ods.get_data(file_path)

# Prendi il primo foglio del file che abbiamo, poi assegna i dati che trova a sheet_data
sheet_name = list(data.keys())[0]
sheet_data = data[sheet_name]

# Andiamo a creare un dataframe, con prima riga i nomi delle colonne e nelle restanti tutti i dati corrispondenti
df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])

# Rimuove eventuali righe vuote
df.dropna(inplace=True)

# Qui costruiamo una funzione che estragga tutti gli hashtag dalla sezione testo, per restituirli in lista
def extract_hashtags(text):
    return re.findall(r'#\w+', text)

# Usiamo lo stesso principio usato per gli hashtag, però per i retweet
def extract_retweeted_user(text):
    match = re.match(r'^RT @(\w+)', text)
    if match:
        return match.group(1)
    else:
        return None

# Dizionari per contare gli hashtag e i retweet per ciascun utente
# Questi sono dizionari annidati, ad esempio nel primo in ciascuna sezione ci saranno utenti e ciascuno avrà un dizionario di hashtag
# I valori assegnati sono predefiniti, verranno poi concretamente assegnati visitando il dataset che abbiamo

user_hashtag_counts = defaultdict(lambda: defaultdict(int))
user_retweet_counts = defaultdict(lambda: defaultdict(int))

# Crea i dizionari inserendo i dati di cui parlavamo sopra
for index, row in df.iterrows():
    username = row['username']
    text = row['text']
    
    hashtags = extract_hashtags(text)
    for hashtag in hashtags:
        user_hashtag_counts[username][hashtag] += 1
    
    retweeted_user = extract_retweeted_user(text)
    if retweeted_user:
        user_retweet_counts[username][retweeted_user] += 1

# Uniamo i due dizionari per ottenere un'unica struttura che contenga sia gli hashtag che i retweet
user_connections = defaultdict(lambda: defaultdict(int))

# Copiamo i conteggi degli hashtag nel nuovo dizionario
for user, hashtags in user_hashtag_counts.items():
    for hashtag, count in hashtags.items():
        user_connections[user][hashtag] = count

# Aggiungiamo i conteggi dei retweet nel nuovo dizionario
for user, retweets in user_retweet_counts.items():
    for retweeted_user, count in retweets.items():
        user_connections[user][retweeted_user] = count

# Costruiamo una lista di tutti gli utenti e hashtag presenti
all_users = list(user_connections.keys())
all_hashtags = set(hashtag for hashtags in user_connections.values() for hashtag in hashtags.keys())

# Costruiamo una matrice di adiacenza che contenga sia gli utenti che gli hashtag
adjacency_matrix = pd.DataFrame(0, index=all_users, columns=all_users+list(all_hashtags))

# Matrice di adiacenza con i conteggi
for user, connections in user_connections.items():
    for connection, count in connections.items():
        adjacency_matrix.loc[user, connection] = count

# Diamo uno stile alla matrice di adiacenza
styled_matrix = adjacency_matrix.style.set_table_styles(
    {
        '': {
            'border': '2px solid black'
        },
        'th': {
            'border': '1px solid black'
        },
        'td': {
            'border': '1px solid black'
        }
    }
).set_properties(**{'border-collapse': 'collapse'})

# Posso usare display poiché ho importato display da iPython
display(styled_matrix)


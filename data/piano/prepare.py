import numpy as np
import os
import pickle

with open("data/piano/all_songs_merged.txt", 'r') as f:
    data = f.read()

# Split the data into words
words = data.split()

print(f"total words: {len(words):,}")

#load the songs_positions list from a pickle file
with open("data/piano/songs_positions.pkl", 'rb') as f:
    songs_positions = pickle.load(f)

# Create a set of unique words
unique_words = set(words)

print(f"unique words: {len(unique_words):,}")

# print(sorted(unique_words))

# Create the stoi (string-to-integer) and itos (integer-to-string) dictionaries
stoi = {word: i for i, word in enumerate(unique_words)}
itos = {i: word for i, word in enumerate(unique_words)}

# Define the vocab size
vocab_size = len(unique_words)

print(f"vocab size: {vocab_size:,}")

# Save the meta information
meta = {'stoi': stoi, 'itos': itos, 'vocab_size': vocab_size}

# Save the meta dictionary as a pickle file
with open('data/piano/meta.pkl', 'wb') as f:
    pickle.dump(meta, f)


# Convert the original data into integer IDs
data_ids = [stoi[word] for word in words]

# Determine the song position where to split
split_song_idx = int(len(songs_positions)*0.9)

# Find the corresponding token position
split_token_idx = songs_positions[split_song_idx][0]

# Split the data_ids into train and val based on the token position
train_ids = data_ids[:split_token_idx]
val_ids = data_ids[split_token_idx:]

print(f"train has {len(train_ids):,} tokens")
print(f"val has {len(val_ids):,} tokens")

# export to bin files
train_ids = np.array(train_ids, dtype=np.uint16)
val_ids = np.array(val_ids, dtype=np.uint16)
train_ids.tofile(os.path.join(os.path.dirname(__file__), 'train.bin'))
val_ids.tofile(os.path.join(os.path.dirname(__file__), 'val.bin'))


from encoding_decoding import *
from random import shuffle,random
import os
import pickle


midi_directory = "AllMidiFiles"
text_directory = "AllMidiTexts"
output_merge_path="data/piano/all_songs_merged.txt"
songs_positions_path="data/piano/songs_positions.pkl"

def transpose_song(song, interval):
    """
    Transpose a song by a certain interval.
    """
    # Create a new list to hold the transposed song
    transposed_song = []

    # Iterate over the words in the song
    for word in song:
        # Check if the word represents a note
        if word.startswith('n'):
            # Extract the note value, add the transposition interval, and construct the new word
            note_value = int(word[1:])
            transposed_note_value = note_value + interval

            # Ensure the transposed note is within the valid range
            while transposed_note_value > 108:
                transposed_note_value -= 12
            while transposed_note_value < 21:
                transposed_note_value += 12

            transposed_word = 'n' + str(transposed_note_value)

            # Add the transposed word to the new song
            transposed_song.append(transposed_word)
        else:
            # If the word does not represent a note, add it to the new song as is
            transposed_song.append(word)

    return ' '.join(transposed_song)


def stretch_song(song, stretch_factor):
    """
    Stretch a song by a certain factor.
    """
    # Create a new list to hold the stretched song
    stretched_song = []

    # Iterate over the words in the song
    for word in song:
        # Check if the word represents a duration
        if word.startswith('d'):
            #check if the previouse word is a note
            if song[song.index(word) - 1].startswith("n"):
                # Extract the duration value, multiply it by the stretch factor, and construct the new word
                duration_value = int(word[1:])
                stretched_duration_value = round(duration_value * stretch_factor)

                # Make sure the stretched duration is at least 1
                stretched_duration_value = max(1, stretched_duration_value)

                stretched_word = 'd' + str(stretched_duration_value)

                # Add the stretched word to the new song
                stretched_song.append(stretched_word)
        else:
            # If the word does not represent a duration, add it to the new song as is
            stretched_song.append(word)

    return ' '.join(stretched_song)


def merge_and_transpose_and_stretch_all_songs(text_directory, output_merge_path, songs_positions_path, intervals, stretch_factors):
    # Get a list of all the filenames in the directory
    filenames = [f for f in os.listdir(text_directory) if f.endswith(".txt")]

    # Shuffle the filenames
    shuffle(filenames)

    # Initialize a counter for the current word position
    current_position = 0

    # Initialize an empty list to hold song positions
    songs_positions = []

    # Open the output file
    with open(output_merge_path, 'w') as out_f:
        # Loop over each shuffled filename
        for filename in filenames:
            try:
                # Open the text file
                with open(os.path.join(text_directory, filename), 'r') as in_f:
                    # Read the song
                    song = in_f.read().split()

                    # get a random fraction 
                    p=random()

                    # Write the song and its position to the file and the list
                    out_f.write(' '.join(song) + " <SEP> ")
                    songs_positions.append((current_position, current_position + len(song)))
                    current_position += len(song) + 1  # Add 1 for the <SEP> token

                    # if p less than or equal to 0.3 then just transpose the song , if it's between 0.3 and 0.6 then just stretch the song , if it's between 0.6 and 1 then transpose and stretch the song 
                    if p<=0.3:
                        print("transposing song")
                        for interval in intervals:
                            transposed_song = transpose_song(song, interval)
                            out_f.write(transposed_song + " <SEP> ")
                            songs_positions.append((current_position, current_position + len(transposed_song.split())))
                            current_position += len(transposed_song.split()) + 1
                    elif p>0.3 and p<=0.6:
                        print("stretching song")
                        for stretch_factor in stretch_factors:
                            stretched_song = stretch_song(song, stretch_factor)
                            out_f.write(stretched_song + " <SEP> ")
                            songs_positions.append((current_position, current_position + len(stretched_song.split())))
                            current_position += len(stretched_song.split()) + 1
                    else:
                        print("transposing and stretching song")   
                        for interval in intervals:
                            transposed_song = transpose_song(song, interval)
                            for stretch_factor in stretch_factors:
                                transposed_and_stretched_song = stretch_song(transposed_song.split(), stretch_factor)
                                out_f.write(transposed_and_stretched_song + " <SEP> ")
                                songs_positions.append((current_position, current_position + len(transposed_and_stretched_song.split())))
                                current_position += len(transposed_and_stretched_song.split()) + 1
                    try:
                        print("Processed file:", filename)
                    except:
                        print("Processed file:", filename.encode('utf-8'))
            except:
                print("Error processing the file!")
                continue

    # Save the songs_positions list to a pickle file
    with open(songs_positions_path, 'wb') as f:
        pickle.dump(songs_positions, f)


# all_midi_to_text(midi_directory, text_directory)
merge_and_transpose_and_stretch_all_songs(text_directory, output_merge_path,songs_positions_path, [-2, 2,-5,5,-1,1,-3,3], [0.5,0.75,1.5])


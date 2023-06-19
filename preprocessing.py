import numpy as np
from math import floor
import music21
import os
import json

def text_to_midi(chordtxt, notetxt):
    with open(chordtxt, "r") as file:
        chordstring = file.read()

    with open(notetxt, "r") as file:
        notestring = file.read()
    score_chord = chordstring.split(" ")
    score_note = notestring.split(" ")
    # define some parameters (from encoding script)
    sample_freq = 12
    note_offset = 33
    ################################
    ##Converting ChordWise strings to array
    # define variables and lists needed for chord decoding
    speed = 1.0 / sample_freq
    piano_notes = []
    violin_notes = []
    time_offset = 0
    # start decoding here
    score = score_chord

    # loop through every timestep / chord
    for i in range(len(score)):
        # skip empty lists
        if len(score[i]) == 0:
            continue

        # skip idx 0 as it indicates instruments
        for j in range(1, len(score[i])):
            # if the note is played, append note to list
            if score[i][j] == "1":
                duration = 2

                # create music21 note object
                new_note = music21.note.Note(j + note_offset)

                # add duration to note object
                new_note.duration = music21.duration.Duration(duration * speed)

                # add timestamp (time offset) to note object
                new_note.offset = (i + time_offset) * speed

                # append note to respective instruments
                if score[i][0] == "p":
                    piano_notes.append(new_note)
                elif score[i][0] == "v":
                    violin_notes.append(new_note)

    # list of all notes for each instrument should be ready at this stage

    # creating music21 instrument objects
    violin = music21.instrument.fromString("Violin")
    piano = music21.instrument.fromString("Piano")

    # insert instrument object to start (0 index) of notes list
    violin_notes.insert(0, violin)
    piano_notes.insert(0, piano)

    # create music21 stream object for individual instruments
    violin_stream = music21.stream.Stream(violin_notes)
    piano_stream = music21.stream.Stream(piano_notes)

    # merge both stream objects into a single stream of 2 instruments
    chord_stream = music21.stream.Stream([violin_stream, piano_stream])

    ################################
    ## Converting NoteWise into array
    # define some parameters (from encoding script)
    sample_freq = 12
    note_offset = 33
    # define variables and lists needed for chord decoding
    speed = 1.0 / sample_freq
    piano_notes = []
    violin_notes = []
    time_offset = 0

    # start decoding here
    score = score_note

    i = 0

    # for outlier cases, not seen in sonat-1.txt
    # not exactly sure what scores would have "p_octave_" or "eoc" (end of chord?)
    # it seems to insert new notes to the score whenever these conditions are met
    while i < len(score):
        if score[i][:9] == "p_octave_":
            add_wait = ""
            if score[i][-3:] == "eoc":
                add_wait = "eoc"
                score[i] = score[i][:-3]
            this_note = score[i][9:]
            score[i] = "p" + this_note
            score.insert(i + 1, "p" + str(int(this_note) + 12) + add_wait)
            i += 1
        i += 1

    # loop through every event in the score
    for i in range(len(score)):
        # if the event is a blank, space, "eos" or unknown, skip and go to next event
        if score[i] in ["", " ", "<eos>", "<unk>"]:
            continue

        # if the event starts with 'end' indicating an end of note
        elif score[i][:3] == "end":
            # if the event additionally ends with eoc, increare the time offset by 1
            if score[i][-3:] == "eoc":
                time_offset += 1
            continue

        # if the event is wait, increase the timestamp by the number after the "wait"
        elif score[i][:4] == "wait":
            time_offset += int(score[i][4:])
            continue

        # in this block, we are looking for notes
        else:
            # Look ahead to see if an end<noteid> was generated
            # soon after.
            duration = 1
            has_end = False
            note_string_len = len(score[i])
            for j in range(1, 200):
                if i + j == len(score):
                    break
                if score[i + j][:4] == "wait":
                    duration += int(score[i + j][4:])
                if (
                    score[i + j][: 3 + note_string_len] == "end" + score[i]
                    or score[i + j][:note_string_len] == score[i]
                ):
                    has_end = True
                    break
                if score[i + j][-3:] == "eoc":
                    duration += 1

            if not has_end:
                duration = 12

            add_wait = 0
            if score[i][-3:] == "eoc":
                score[i] = score[i][:-3]
                add_wait = 1

            try:
                new_note = music21.note.Note(int(score[i][1:]) + note_offset)
                new_note.duration = music21.duration.Duration(duration * speed)
                new_note.offset = time_offset * speed
                if score[i][0] == "v":
                    violin_notes.append(new_note)
                else:
                    piano_notes.append(new_note)
            except:
                print("Unknown note: " + score[i])

            time_offset += add_wait

    # list of all notes for each instrument should be ready at this stage

    # creating music21 instrument objects
    violin = music21.instrument.fromString("Violin")
    piano = music21.instrument.fromString("Piano")

    # insert instrument object to start (0 index) of notes list
    violin_notes.insert(0, violin)
    piano_notes.insert(0, piano)

    # create music21 stream object for individual instruments
    violin_stream = music21.stream.Stream(violin_notes)
    piano_stream = music21.stream.Stream(piano_notes)

    # merge both stream objects into a single stream of 2 instruments
    note_stream = music21.stream.Stream([violin_stream, piano_stream])
    chord_stream.write("midi", fp="samples/ChordWise.mid")

    note_stream.write("midi", fp="samples/NoteWise.mid")


def midi_to_text(
    fname,
    sample_freq=16,
    note_range=127,
    note_offset=0,
    notewise_folder="text/notewise",
):
    song_name = os.path.basename(fname)
    song_name = os.path.splitext(song_name)[0]
    mf = music21.midi.MidiFile()
    mf.open(fname)
    mf.read()
    mf.close()
    s = music21.converter.parse(fname)
    maxTimeStep = floor(s.duration.quarterLength * sample_freq) + 1
    score_arr = np.zeros((maxTimeStep, 1, note_range))
    # define two types of filters because notes and chords have different structures for storing their data
    # chord have an extra layer because it consist of multiple notes

    noteFilter = music21.stream.filters.ClassFilter("Note")
    chordFilter = music21.stream.filters.ClassFilter("Chord")
    # pitch.midi-note_offset: pitch is the numerical representation of a note.
    #                         note_offset is the the pitch relative to a zero mark. eg. B-=25, C=27, A=24

    # n.offset: the timestamps of each note, relative to the start of the score
    #           by multiplying with the sample_freq, you make all the timestamps integers

    # n.duration.quarterLength: the duration of that note as a float eg. quarter note = 0.25, half note = 0.5
    #                           multiply by sample_freq to represent duration in terms of timesteps
    notes = []
    instrumentID = 0
    # Constants for binning velocities
    SLOW_THRESHOLD = 42  # Define according to your requirements
    FAST_THRESHOLD = 85  # Define according to your requirements

    for n in s.recurse().addFilter(noteFilter):
        notes.append(
                (n.pitch.midi - note_offset,
                floor(n.offset * sample_freq),
                floor(n.duration.quarterLength * sample_freq),
                instrumentID,
                n.volume.velocity)
            )
    # do the same using a chord filter

    for c in s.recurse().addFilter(chordFilter):
        # unlike the noteFilter, this line of code is necessary as there are multiple notes in each chord
        # pitchesInChord is a list of notes at each chord eg. (<music21.pitch.Pitch D5>, <music21.pitch.Pitch F5>)
        pitchesInChord = c.pitches
        # do same as noteFilter and append all notes to the notes list
        for p in pitchesInChord:
            notes.append(
                (
                    p.midi - note_offset,
                    floor(c.offset * sample_freq),
                    floor(c.duration.quarterLength * sample_freq),
                    instrumentID,
                    c.volume.velocity
                )
            )
    # the variable/list "notes" is a collection of all the notes in the song, not ordered in any significant way

    for n in notes:
        # pitch is the first variable in n, previously obtained by n.midi-note_offset
        pitch = n[0]

        # do some calibration for notes that fall our of note range
        # i.e. less than 0 or more than note_range
        while pitch < 0:
            pitch += 12
        while pitch >= note_range:
            pitch -= 12

        # 3rd element refers to instrument type => if instrument is violin, use different pitch calibration
        if n[3] == 1:  # Violin lowest note is v22
            while pitch < 22:
                pitch += 12

        # start building the 3D-tensor of shape: (796, 1, 38)
        # score_arr[0] = timestep
        # score_arr[1] = type of instrument
        # score_arr[2] = pitch/note out of the range of note eg. 38

        # n[0] = pitch
        # n[1] = timestep
        # n[2] = duration
        # n[3] = instrument

        score_arr[n[1], n[3], pitch] = 1  # Strike note
        score_arr[n[1] + 1 : n[1] + n[2], n[3], pitch] = 2  # Continue holding note

    instr = {}
    instr[0] = "p"
    instr[1] = "v"

    score_string_arr = []

    # loop through all timesteps
    for timestep in score_arr:
        # selecting the instruments: i=0 means piano and i=1 means violin
        for i in list(
            reversed(range(len(timestep)))
        ):  # List violin note first, then piano note
            #
            score_string_arr.append(
                instr[i] + "".join([str(int(note)) for note in timestep[i]])
            )

    modulated = []
    # get the note range from the array
    note_range = len(score_string_arr[0]) - 1

    for i in range(0, 12):
        for chord in score_string_arr:
            # minus the instrument letter eg. 'p'
            # add 6 zeros on each side of the string
            padded = "000000" + chord[1:] + "000000"

            # add back the instrument letter eg. 'p'
            # append window of len=note_range back into
            # eg. if we have "00012345000"
            # iteratively, we want to get "p00012", "p00123", "p01234", "p12345", "p23450", "p34500", "p45000",
            modulated.append(chord[0] + padded[i : i + note_range])

    # input of this function is a modulated string
    long_string = modulated

    translated_list = []

    # for every timestep of the string
    for j in range(len(long_string)):
        # chord at timestep j eg. 'p00000000000000000000000000000000000100'
        chord = long_string[j]
        next_chord = ""

        # range is from next_timestep to max_timestep
        for k in range(j + 1, len(long_string)):
            # checking if instrument of next chord is same as current chord
            if long_string[k][0] == chord[0]:
                # if same, set next chord as next element in modulation
                # otherwise, keep going until you find a chord with the same instrument
                # when you do, set it as the next chord
                next_chord = long_string[k]
                break

        # set prefix as the instrument
        # set chord and next_chord to be without the instrument prefix
        # next_chord is necessary to check when notes end
        prefix = chord[0]
        chord = chord[1:]
        next_chord = next_chord[1:]

        # checking for non-zero notes at one particular timestep
        # i is an integer indicating the index of each note the chord
        for i in range(len(chord)):
            if chord[i] == "0":
                continue

            # set note as 2 elements: instrument and index of note
            # examples: p22, p16, p4
            note = prefix + str(i) +":v"+str(n[4])

            # if note in chord is 1, then append the note eg. p22 to the list
            if chord[i] == "1":
                translated_list.append(note)

            # If chord[i]=="2" do nothing - we're continuing to hold the note

            # unless next_chord[i] is back to "0" and it's time to end the note.
            if next_chord == "" or next_chord[i] == "0":
                translated_list.append("end" + note)

        # wait indicates end of every timestep
        if prefix == "p":
            translated_list.append("wait")

    # this section transforms the list of notes into a string of notes

    # initialize i as zero and empty string
    i = 0
    translated_string = ""

    while i < len(translated_list):
        # stack all the repeated waits together using an integer to indicate the no. of waits
        # eg. "wait wait" => "wait2"
        wait_count = 1
        if translated_list[i] == "wait":
            while (
                i + wait_count < len(translated_list)
                and translated_list[i + wait_count] == "wait"
            ):
                wait_count += 1
            translated_list[i] = "wait" + str(wait_count)

        # add next note
        translated_string += translated_list[i] + " "
        i += wait_count

    print("chordwise encoding type and length:", type(modulated), len(modulated))
    print(
        "notewise encoding type and length:",
        type(translated_string),
        len(translated_string),
    )
    # default settings: sample_freq=12, note_range=62
    notewise_folder = "test_song/NoteWise"
    chordwise_folder = "test_song/ChordWise"

    # create notewise_folder if it does not exist
    if not os.path.exists(notewise_folder):
        os.makedirs(notewise_folder)
    
    if not os.path.exists(chordwise_folder):
        os.makedirs(chordwise_folder)

    # export notewise encoding
    f = open(os.path.join(notewise_folder, song_name+".txt"), "w+")
    f.write(translated_string)
    f.close()

    # export chordwise encoding
    f = open(os.path.join(chordwise_folder, song_name+".txt"), "w+")
    f.write(" ".join(modulated))
    f.close()


#function to convert all midi files in a directory to text files
def process_midi_files(root_dir):
    # Walk through root directory
    for dir_name, _, file_list in os.walk(root_dir):
        for file_name in file_list:
            # Check if file is a .midi file
            if file_name.endswith('.mid'):
                # Construct full file path
                full_path = os.path.join(dir_name, file_name)
                # Process .midi file
                try:
                    midi_to_text(full_path)
                except Exception as e:
                    print(f"Error processing {full_path}: {e}")


def replace_last_wait(filename):
    with open(filename, 'r') as f:
        text = f.read()

    # Split the text into tokens
    tokens = text.split()

    # Find the index of the last 'wait' command in the tokens list
    # Here we use a generator expression to find the last token starting with 'wait'
    last_wait_index = next(i for i in reversed(range(len(tokens))) if tokens[i].startswith('wait'))

    # Replace the last 'wait' command with 'ENDSONG'
    tokens[last_wait_index] = 'ENDSONG'

    # Join the tokens back into a string
    new_text = ' '.join(tokens)

    # Write the new text back to the file
    with open(filename, 'w') as f:
        f.write(new_text)

# specify your directory path here
directory_path = r'test_song\NoteWise'

# output file
output_file_path = r'data\piano\piano.txt'

# initialize an empty string
all_documents = ""

# loop over each file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".txt"):  # ensure you're working with text files
        # open the text file
        with open(os.path.join(directory_path, filename), 'r') as f:
            # read the file and append its contents to the string, with <SEP> at the end
            all_documents += f.read() + " <SEP> "
            print("Read file:", filename)

# remove the last <SEP> from the string (optional)
all_documents = all_documents.rstrip(" <SEP> ")

# write all the documents to a new file
with open(output_file_path, 'w') as f:
    f.write(all_documents)




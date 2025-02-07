
# nanoGPT for piano :musical_keyboard:

This project extends the foundational work of Andrej Karpathy's nanoGPT, which focused on creating and training a GPT-2-based model. In our case, I have developed a graphical user interface (GUI) using the Pygame library to interact with a modified version of a GPT-2-like model. My adaptation differs from the original nanoGPT in that it functions at the word level, as opposed to the character level.

In the scope of this project, the term "word" is specialized to mean one of two musical elements:
1) A pitch or a rest
2) The duration associated with that pitch or rest
   
Through the GUI, users have the option to:
1) Generate a completely new musical piece based on the model's training.
2) Create a continuation of a random song from the dataset on which the model was trained and also retry the continuation of the same song.

Additionally, the GUI offers controls for adjusting various parameters of the model's generation process, including:
1) Temperature: This affects the model's level of "creativity" in generating the piece.
2) Number of Tokens to Generate: This specifies the length of the generated output.
3) Top K Tokens: Users can select the top 'K' tokens to be considered during the generation process, while all other tokens are assigned a probability of zero.

## Install :gear:

```
pip install torch numpy transformers datasets pygame pygame_gui pretty_midi music21
```

Dependencies:

-  'PyTorch'
-  'numpy'
-  'transformers' for huggingface transformers  (to load GPT-2 checkpoints)
-  'datasets' for huggingface datasets (if you want to download + preprocess OpenWebText)
-  'pygame'
-  'pygame_gui'
-  'pretty_midi'
-  'music21'


## GUI :computer:

- You can control each slider as you like
- Press an option from below :
     1) New Piece
     2) Continue Song (Retry Song works only if the last generation was from pressing the Continue Song button )
- After selecting an option, press Generate and wait until the text says Generation Complete! , and then you can press play to listen to the piece generated. 
  Also, the piano roll visual of the generated piece appears below :).

![Example Image](./ML_Piano_Gui.png)


## Loss plots :chart_with_downwards_trend:

Due to my humble computation resources of only 1 GPU on my laptop, I only trained two models ( 5.6M and 13M parameters ) . Trying to train bigger models would be so slow and take a lot of time, my laptop might catch on fire if trained for too long on big models haha

- 5.6M model
  ** 3 Layers, 6 Heads, 384 embedding **

![Example Image](./piano-model-5.63M/loss_plot.png)

** The spike is because I changed the learning rate by mistake in an interval of time-steps during training 


- 13M model
  ** 4 Layers, 8 Heads, 512 embedding **

![Example Image](./piano-model-13M/loss_plot.png)

As we can see the 13M model performed better, this is an indication that more Layers/Heads can lead to better results. Adding more Layers can make the model capture and learn more complex patterns, Adding more heads can increase the attention to how different tokens affect/interact with each other in the input ( Input used is of size 200 tokens ). A better environment with better computation resources would allow further Hyperparameter tuning in hopes of achieving lower val/training loss.


## Encoding & Decoding MIDI to Text and Vice-Versa: :musical_note::left_right_arrow::abc:

- **Encoding from MIDI to Text**
   - **Reading MIDI**: Utilizes the `music21` library to parse the MIDI files.
   - **Pitch and Duration**: Iterates through the notes and chords to gather their pitch and duration.
   - **Piano-Roll Array**: Declares a piano-roll array where rows correspond to time-frequency windows and columns correspond to the range of pitches.
     - Places a '1' in the row corresponding to a note's start time and '2' in subsequent rows to indicate the note is sustained.
   - **Text Conversion**: Translates the filled array into words. Notes are denoted as `n[pitch] d[duration]` and rests are denoted by `sepxx`.
  
- **Decoding from Text to MIDI**
   - **Reading Text**: Parses the text representation starting with the token `START` and ending with `END`.
   - **Array Conversion**: Converts the parsed text back into a piano-roll array.
   - **MIDI Generation**: Uses the `music21` library to convert the array back into a MIDI file.

- **Example Text Encoding**
   - A sample text encoding might look like:
     ```
     START n60 d5 n62 d3 sepxx d2 n65 d4 END
     ```
   - In this example:
     - `START` and `END` are tokens that signify the beginning and end of the text.
     - `n60 d5` denotes a note with a pitch of 60 lasting for 5 time steps.
     - `sepxx d2` represents a rest or no-note situation lasting for 2 time steps.


## Data Augmentation Techniques for Music :twisted_rightwards_arrows:

Data augmentation is crucial in machine learning models for music generation to improve their ability to generalize from the training set to unseen data. Below are the techniques used and why they are effective for musical data:

### Transposition
- **Description**: Shifts the pitch of each note in the song by a certain interval.
- **Key Point**: Ensures that the transposed notes stay within a valid range (21-108).
- **Why it works for music**: Transposing a song doesn't change its harmonic structure but presents it in a different key, thereby allowing the model to learn the song's structure independent of its key.

### Stretching
- **Description**: Alters the duration of each note in the song by a given stretch factor.
- **Key Point**: The duration of a note after stretching is rounded and is at least 1.
- **Why it works for music**: Stretching time can simulate different tempos, teaching the model to recognize the same patterns at varying speeds.

### Example

In this example, the transposition of a note with pitch 60 by an interval of +2 would result in a note with pitch 62. Similarly, stretching a note with a duration of 5 by a stretch factor of 0.5 would result in a new duration of 3 (rounded).


## Acknowledgments :clap:

### Repositories
- **nanoGPT by Andrej Karpathy**: Forked this repository to adapt and build upon its foundational GPT-2-based model. [nanoGPT](https://github.com/karpathy/nanoGPT)

### Datasets
- **ADL Piano MIDI**: Utilized this dataset for training and testing the model. [Dataset](https://paperswithcode.com/dataset/adl-piano-midi)



## Demo Video :movie_camera:

A demonstration video of the project is available in a ZIP file named "Video Demonstration." Download it to see the project in action.

## The model is not uploaded in the repo due to size . 

## Note on Commits :exclamation:

> :warning: **Important:** Most of the initial work on this project was done locally and therefore, the commit history may not fully reflect the development timeline. This is largely due to the constraints of working with a large data set.



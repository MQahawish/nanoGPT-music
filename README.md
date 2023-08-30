
# nanoGPT for piano

This project extends the foundational work of Andrej Karpathy's nanoGPT, which focused on creating and training a GPT-2-based model. In our case, we have developed a graphical user interface (GUI) using the Pygame library to interact with a modified version of a GPT-2-like model. Our adaptation differs from the original nanoGPT in that it functions at the word level, as opposed to the character level.

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

## install

```
pip install torch numpy transformers datasets pygame pygame_gui pretty_midi music21
```

Dependencies:

-  'pytorch'
-  'numpy'
-  'transformers' for huggingface transformers  (to load GPT-2 checkpoints)
-  'datasets' for huggingface datasets (if you want to download + preprocess OpenWebText)
-  'pygame'
-  'pygame_gui'
-  'pretty_midi'
-  'music21'

## quick start

to easily run the program , just run the UI_Pygame.py script either using the IDE or cmd , which opens the gui and starts the program . (it might take a a little bit of time to load , since it needs to load a 13M parameter model :D )


## GUI

 *) You can control each slider as you like
 *) Press an option from below : New Piece , Continue Song (Retry Song works only if the last generation was from pressing Continue Son button )
    after selecting an option , press Generate and wait until the text says Generation Complete! , and then you can press play to listen to the piece generated . 
    Also , the piano roll visual of the generated piece appears below :).

    






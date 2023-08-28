import time
from encoding_decoding import txt2midi
import os
import pickle
from contextlib import nullcontext
import torch
from model import GPTConfig, GPT
from music21 import *
import random

def fix_model_gen(text):
    # if first move is START and last move is END, remove them
    if text.startswith("START"):
        text = text[6:]
    if text.endswith("END"):
        text = text[:-4]
    words = text.split()
    # iterate over the word while keeping track if the tokens alternate between sepxx/nX and dY. once this patterns break , remove everything from that point on
    

    for word in words:
        if word == "END":
            # if the previous word is a dY , and the next word is a dX , make word sepxx
            if words[words.index(word) - 1].startswith("d") and words[words.index(word) + 1].startswith("d"):
                words[words.index(word)] = "sepxx"
            if words[words.index(word) - 1].startswith("d") and words[words.index(word) + 1].startswith("n"):
               #remove the word
                words.remove(word)

    # print if there is an odd number of words
    if len(words) % 2 == 1:
        # remove the last word if there is an odd number of words
        words = words[:-1]
    pairs = []
    for i in range(len(words)):
        if i % 2 == 0:
            pairs.append([words[i], words[i + 1]])
    # construct the text again by concatenating the pairs
    text = ""
    for pair in pairs:
        # if pair[0].startswith("d") and !pair[1].startswith("") , and flip them if so
        if pair[0].startswith("d") and not pair[1].startswith("d"):
            temp = pair[0]
            pair[0] = pair[1]
            pair[1] = temp
        text += pair[0] + " " + pair[1] + " "
    return text

class MidiGenerator:
    def __init__(self,out_dir="piano-model",device='cuda',temperature=1.1,top_k=100,max_new_tokens=500):
        self.device = device 
        self.device_type = 'cuda' if 'cuda' in self.device else 'cpu' 
        self.dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        self.dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16  # or set to torch.float32 or whatever you prefer
        self.ctx = nullcontext() if self.device_type == 'cpu' else torch.cuda.amp.autocast(enabled=True, dtype=self.dtype)
        self.init_from = 'resume' 
        self.out_dir = out_dir
        self.temperature = temperature
        self.top_k = top_k 
        self.max_new_tokens = max_new_tokens
        self.all_files = [f for f in os.listdir('AllMidiTexts') if f.endswith('.txt')]

        # Load your data and model here
        self.model = self.load_model()
    

    def set_device(self, device):
        self.device = device
        self.device_type = 'cuda' if 'cuda' in self.device else 'cpu' 
        self.dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        self.dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    
    def set_temperature(self, temperature):
        self.temperature = temperature
    
    def set_top_k(self, top_k):
        self.top_k = top_k

    def set_max_new_tokens(self, max_new_tokens):
        self.max_new_tokens = max_new_tokens


    def load_model(self):
        torch.manual_seed(1337)
        torch.cuda.manual_seed(1337)
        torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
        torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn

        ckpt_path = os.path.join(self.out_dir, 'ckpt.pt')
        checkpoint = torch.load(ckpt_path, map_location=self.device)
        gptconf = GPTConfig(**checkpoint['model_args'])
        model = GPT(gptconf)
        state_dict = checkpoint['model']
        unwanted_prefix = '_orig_mod.'
        for k,v in list(state_dict.items()):
            if k.startswith(unwanted_prefix):
                state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
        model.load_state_dict(state_dict)

        model.eval()
        model.to(self.device)

        meta_path = os.path.join('data', checkpoint['config']['dataset'], 'meta.pkl')
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)
        stoi, itos = meta['stoi'], meta['itos']
        self.encode = lambda s: [stoi[c] for c in s.split()]
        self.decode = lambda l: ' '.join([itos[i] for i in l])

        return model

    def generate_midi(self,selected_option,bpm=120):
        response = ""
        song_name = ""
        # Generate a new midi file using the loaded model and data.
        if selected_option == 'New Piece':
            start="sepxx"
            response = "This a new piece the model generated" 
            song_name = ""
        if selected_option == 'Continue Song':
            selected_file = random.choice(self.all_files)
            with open(os.path.join('AllMidiTexts', selected_file), 'r') as f:
                song_text = f.read()
            #remove the txt extension
            selected_file = selected_file[:-4]
            response = "This is a continuation of the song:"
            song_name = selected_file
            #get the first 100 tokens of the song, and not 100 letters
            song_text = song_text.split()
            start = ""
            for i in range(100):
                start += song_text[i] + " "
            #remove START token
            start = start[6:]
        start_ids = self.encode(start)
        x = (torch.tensor(start_ids, dtype=torch.long, device=self.device)[None, ...])

        with torch.no_grad():
            if self.device_type == 'cuda':
                with torch.cuda.amp.autocast(enabled=True, dtype=self.dtype):
                    y = self.model.generate(x, 500, temperature=self.temperature, top_k=self.top_k)
            else:
                y = self.model.generate(x, 500, temperature=self.temperature, top_k=self.top_k)
            predicted_text = self.decode(y[0].tolist())
            txt2midi(fix_model_gen(predicted_text), "samples",bpm=bpm)
        return response,song_name




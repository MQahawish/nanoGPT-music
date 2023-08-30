out_dir = "piano-model-13M"
eval_interval = 250 # keep frequent because we'll overfit
eval_iters = 200
log_interval = 1 # don't print too too often

# we expect to overfit on this small dataset, so only save when val improves
always_save_checkpoint = False
init_from = 'resume'
dataset = 'piano'
gradient_accumulation_steps = 4
batch_size = 64
block_size = 200 # context of up to 150 previous wo

# baby GPT model :)
n_layer= 3
n_head= 6
n_embd= 384
dropout= 0.1

learning_rate = 0.000001 # with baby networks can afford to go a bit higher
max_iters = 500000 
lr_decay_iters = 25000 # make equal to max_iters usually
min_lr = 0.00000001 # learning_rate / 10 usually
beta2 = 0.99 # make a bit bigger because number of tokens per iter is small

warmup_iters = 1000 # not super necessary potentially

# on macbook also add
device = 'cuda'  # run on cpu only
compile = False # do not torch compile the model

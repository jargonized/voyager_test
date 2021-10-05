"""After completing a hyperparameter tuning sweep,
(gen_train_sweep.py), this code takes the series 
of saved models, and creates a series of Condor 
scripts to generate a ChampSim prefetch trace for 
each model.

A file that lists each launch condor config line-by-line
is saved to {BASE_DIR}/condor_configs_generate.txt. You
like Quangmire/condor/condor_submit_batch.py to launch them.

Based on: github.com/Quangmire/condor/condor_pc.py
"""


import os
import itertools
import copy
import yaml

from condor_common import generate # Used for template for condor submit scripts

VOYAGER_PATH = '/u/cmolder/GitHub/voyager/'
BASE_CONFIG_PATH = '/u/cmolder/GitHub/voyager/configs/base_mod_lstm.yaml'
BASE_DIR = '/scratch/cluster/cmolder/voyager_hypertuning/lstm/'
USE_GPU = True
PRINT_EVERY = 100 # Number of steps between printing to log

TRACE_DIR = '/scratch/cluster/qduong/ML-DPC/data/load_traces/'
TRACES = [
    'spec17/605.mcf-s0.txt.xz',
]

VARIATIONS = {
    # - learningrate_batchsize/
    #'learning_rate': [0.01, 0.001, 0.0001, 0.00001], # best mcf-s0: 0.001 (run 1)
    #'batch_size': [32, 64, 128, 256, 512],           # best mcf-s0: 512   (run 1)
    # - embeddingsizes/
    #'pc_embed_size': [16, 32, 64, 128, 256],         # (pc=128, page=512, bsz=512) runs out of memory on GTX 1080
    #'page_embed_size': [32, 64, 128, 256]
    # - experts_lrdecay/
    #'page_embed_size': [64, 256],
    #'num_experts': [10, 25, 50, 75, 100],
    #'learning_rate_decay': [1, 2] # 1 disables LR decay
    # - lstm/
    'lstm_dropout': [0.6, 0.8],
    'lstm_size': [32, 64, 128, 256],
    'lstm_layers': [1, 2],
}

# Template for bash script
SH_TEMPLATE = '''#!/bin/bash
source /u/cmolder/miniconda3/etc/profile.d/conda.sh
conda activate tensorflow
python3 -u {script_file} --benchmark {benchmark} \\
    --config {config_file}  \\
    --prefetch-file {prefetch_file} \\
    --model-path {model_path} --print-every {print_every} \\
'''


def permutation_string(permutation):
    """Generate a string representing the permutation."""
    pm_str = ''
    for k, v in permutation.items():
        pm_str += f'{k}-{v}_'
    return pm_str.rstrip('_')


def permute_variations(variations):
    """Generate all permutations of the variations."""
    keys, values = zip(*variations.items())
    permutations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return permutations
    

def main():
    # Open base config and get it as a dictionary
    with open(BASE_CONFIG_PATH, 'r') as f:
        base_config = yaml.safe_load(f)
    print(f'Base config: {base_config}')

    # Generate all permutations of the variations.
    permutations = permute_variations(VARIATIONS)
    print(f'Generating {len(permutations)} configurations.')

    # Track condor files generated so they can be batch launched later
    # (paths saved line-by-line into the same file)
    condor_files = []

    # For each trace, generate each permuted configuration and its script.
    for tr in TRACES:
        for pm in permutations:
            tr_name, pm_name = tr.split('.')[1], permutation_string(pm)

            # Setup initial output directories/files per experiment
            tensorboard_dir = os.path.join(BASE_DIR, 'tensorboard', tr_name, 'generate', pm_name + '/')
            log_file_base = os.path.join(BASE_DIR, 'logs', tr_name, 'generate', pm_name)
            config_file = os.path.join(BASE_DIR, 'configs', f'{pm_name}.yaml')
            condor_file = os.path.join(BASE_DIR, 'condor', tr_name, 'generate', f'{pm_name}.condor')
            script_file = os.path.join(BASE_DIR, 'scripts', tr_name, 'generate', f'{pm_name}.sh')
            model_file = os.path.join(BASE_DIR, 'models', tr_name, f'{pm_name}.model')
            prefetch_file = os.path.join(BASE_DIR, 'prefetch_traces', tr_name, f'{pm_name}.txt')
            
            print(f'\nFiles for {tr_name}, {pm_name}:')
            print(f'    output log  : {log_file_base}.OUT')
            print(f'    error log   : {log_file_base}.ERR')
            print(f'    model       : {model_file}')
            print(f'    condor      : {condor_file}')
            print(f'    script      : {script_file}')
            print(f'    prefetches  : {prefetch_file}')

            # Create directories
            os.makedirs(tensorboard_dir, exist_ok=True)
            os.makedirs(os.path.join(BASE_DIR, 'logs', tr_name, 'generate'), exist_ok=True)
            os.makedirs(os.path.join(BASE_DIR, 'configs'), exist_ok=True)
            os.makedirs(os.path.join(BASE_DIR, 'condor', tr_name, 'generate'), exist_ok=True)
            os.makedirs(os.path.join(BASE_DIR, 'scripts', tr_name, 'generate'), exist_ok=True)
            os.makedirs(os.path.join(BASE_DIR, 'models', tr_name), exist_ok=True)
            os.makedirs(os.path.join(BASE_DIR, 'prefetch_traces', tr_name), exist_ok=True)

            # Build condor file
            condor = generate(
                gpu=USE_GPU,
                err_file=log_file_base + '.ERR',
                out_file=log_file_base + '.OUT',
                init_dir=VOYAGER_PATH,
                exe=script_file
            )
            with open(condor_file, 'w') as f:
                print(condor, file=f)
     

            # Build script file
            with open(script_file, 'w') as f:
                print(SH_TEMPLATE.format(
                    script_file=os.path.join(VOYAGER_PATH, 'generate.py'),
                    benchmark=os.path.join(TRACE_DIR, tr),
                    config_file=config_file,
                    model_path=model_file,
                    prefetch_file=prefetch_file,
                    print_every=PRINT_EVERY
                ), file=f)
            os.chmod(script_file, 0o777) # Make script executable

            condor_files.append(condor_file) # Add condor file to the list

    print(f'\nCondor file list : {os.path.join(BASE_DIR, "condor_configs_generate.txt")}')
    with open(os.path.join(BASE_DIR, 'condor_configs_generate.txt'), 'w') as f:
        for cf in condor_files:
            print(cf, file=f)


if __name__ == '__main__':
    main()

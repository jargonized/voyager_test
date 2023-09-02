# Voyager

Voyager Data Prefetcher implemented in TensorFlow 2:

> Zhan Shi, Akanksha Jain, Kevin Swersky, Milad Hashemi, Parthasarathy Ranganathan, and Calvin Lin. 2021. A hierarchical neural model of data prefetching. In Proceedings of the 26th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS 2021). Association for Computing Machinery, New York, NY, USA, 861–873. DOI:https://doi.org/10.1145/3445814.3446752

Adapted from [https://github.com/aleczhanshi/neural_hierarchical_sequence](https://github.com/aleczhanshi/neural_hierarchical_sequence)

# Implemented Features
- Voyager model
- Multi-Labeling Scheme
  - PC Localization
  - Deltas
  - Spatial Localization
- Generation code for simulating with the modified ChampSim for the ML
  Prefetching Competition at [https://github.com/Quangmire/ChampSim](https://github.com/Quangmire/ChampSim)

# Missing Features
- Fine-Tuned Hyperparameters
- Online Training

# Extra Features
- seq2seq Sequence Loss

# Input data format
```Unique Instr Id, Cycle Count, Load Address, Instruction Pointer of the Load, LLC hit/miss```
### sample data
``` 4, 15, 28e837c88340, 406a82, 0
7, 261, 28e837c86f40, 406a8e, 0
17, 277, fdfd3a8c3bc0, 406abc, 0
29, 278, fdfd3a8c4200, 7b5749, 0
18, 610, fdfd3a8c5d80, 406abf, 0
24, 945, fdfd3a8c6dc0, 7b5730, 0
60, 1122, fdfd3a8c6f00, 7b1aeb, 0 ```

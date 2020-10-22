# Running an Algorithm
Before one can run an algorithm, first the following needs to be installed: 
1. Python 3 (Python 3.7.3 was used for the experiments)
2. numpy (can be installed via pip using: `pip install --user numpy`)
3. numpyencoder (can be installed via pip using: `pip install --user numpyencoder`)

Two python files are located in the root folder than are used to run the experiments 
used in the thesis: `evaluate_algorithm.py` and `evaluate_heuristic`. The first script
is used to evaluate the ADP approaches. The second file is used to evaluate the selected
heuristics. Each file has a set of flags that can be used to change settings in the 
run algorithm. 

## ADP (`evaluate_algorithm.py`)
The following command line arguments are available when running `evaluate_algorithm.py`:
- **-N**, _default=151_. The number of training iterations run +1. A value of 151 yields 150 iterations.
- **-e**, _default=150_. The number of evaluation runs during evaluating.
- **-i**, _default=10_. Every i'th iteration an evaluation is run
- **-c**, _required_. The number of processes the program is allowed to spawn. 
In other words, the number of cores used. Each problem instance is run in parallel. 
Specifying a number higher than the number of problem instances does not speed up the evaluation.  
- **-a**, _required_. The algorithm evaluated. Available algorithms:     
    - SingleFixed, _single pass with fixed stepsize_
    - SingleHarmonic, _single pass with harmonic stepsize_
    - DoubleFixed, _double pass with fixed stepsize_
    - DoubleHarmonic, _double pass with harmonic stepsize_
    - VFA1, VFA2, VFA3, VFA4, VFA5, VFA6, _respective basis function_
- **-t**, _required_. Which terminal type is evaluated. Available options are: 
    - 1, _gantry terminal_
    - 2, _reach stacker terminal_
    - 3, _real life small_
    - 4, _real life medium_
    - 5, _real life big_
    - 6, _real life tiny_
- **-discount**, _default=1_. The value of the discount factor
- **-delta**, _default=0.9_. The value of delta
- **-weight**, _default=1_. The value of the initial wheights of the feature function
- **-epsilon**, _default=0.05_. The value of epsilon (epsilon greedy)
- **-constant**, _default=1_. The value of the constant feature

Make sure that the indicated terminal layout is present in the events list. In addition, 
the results of the run are written to the `evaluation` folder (if not present it will
be created). In this folder, the results of each algorithm on each instance is located 
under the folder by the name of the algorithm. The algorithm name will contain the paramaters 
used when a different value than the default is picked. The folder `final` within `evaluation` 
will contain the final results of each algorithm. 

## Heuristic
The following command line arguments are available when running `evaluate_heuristic.py`:
- **-e**, _default=150_. The number of evaluation runs during evaluating.
- **-a**, _required_. The algorithm evaluated. Available algorithms:     
    - Myopic, _The Myopic approach_
    - MM, _The Min-Max Heuristic_
    - MMAdopted, _The adopted version of MM_
- **-t**, _required_. Which terminal type is evaluated. Available options are: 
    - 1, _gantry terminal_
    - 2, _reach stacker terminal_
    - 3, _real life small_
    - 4, _real life medium_
    - 5, _real life big_
    - 6, _real life tiny_

Make sure that the indicated terminal layout is present in the events list. In addition, 
the results of the run are written to the `evaluation` folder (if not present it will
be created). In this folder, the results of each algorithm on each instance is located 
under the folder by the name of the algorithm. The algorithm name will contain the paramaters 
used when a different value than the default is picked. The folder `final` within `evaluation` 
will contain the final results of each algorithm. 


# Problem Instances
The problem instances used for the thesis are located in the folder `events`. 
Each problem instance is saved as a JSON file with a single JSON object. 
This object has 3 keys: `events`, `training_events` and `evaluating_events`. 
Each object is discussed in more detail below. 

The file name indicates what parameters are used to generate the instance. The format
is as follows:
`{time-periods}_{dwell-time}_{number-of-inbound-containers}_{number_of_samples}_{instance-number}.json`



## Events
The events is a JSON list. This list contains multiple batches (also a JSON list).
Each batch consist in turn out of containers. A container, again, is a JSON list.
Both types are explained in more details in the sections below. The events denote the 
problem instance as it contains all the batches (in order) and all containers belonging
to these batches.

### Batch
A batch is a list of containers. Each batch is either inbound or outbound. This means that
all containers within a batch are inbound or outbound (never mixed). The index of the batch
indicate wether the batch is in- or out-bound. An even index (0, 2, 4, ...) denotes an inbound batch.
An uneven number indicates a outbound batch. 

### Container
A container is always a JSON list consisting out of three integer elements. 
The first element is the ID of the container. This is unique between all containers.
The second element denotes the batch in which this container departs. Using this number,
the index of the outbound batch can be calculated. _Example:_ a container its batch 
label is 5. This means that the index of the batch in which this container departs is `5*2+1=11`.
The third element indicates the order number within a batch. At the time of planning,
the order of a batch is not yet known. Therefore all order numbers are set to -1 to
indicate that the order is not yet known. 


## Training Events
For each problem instance, 250 training samples are generated. Therefore, the training 
events is a JSON list of realisations. A realisation is formatted the same as an problem 
instance (both a list of batches), but now the order within a batch is set. 

## Evaluating Events 
For each problem instance, 250 evaluating samples are generated. Therefore, the evaluating 
events is a JSON list of realisations. A realisation is formatted the same as an problem 
instance (both a list of batches), but now the order within a batch is set. 

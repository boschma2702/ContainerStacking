import argparse
from multiprocessing import Pool
from typing import List, Tuple

import numpy

from main.model.adp.fileWriter import FileWriter
from main.model.adp.stepsize import Harmonic, Fixed
from main.model.adp.valuefunctions.abstract_state import AbstractState
from main.model.adp.valuefunctions.basisfunction import BasisFunction
from main.model.adp.valuefunctions.features.averageStackHeight import average_stack_height
from main.model.adp.valuefunctions.features.batchLabelDifference import batch_label_difference
from main.model.adp.valuefunctions.features.blockingContainers import blocking_containers
from main.model.adp.valuefunctions.features.compositeMeasure import composite_measure, composite_adopted_measure
from main.model.adp.valuefunctions.features.constant import constant, constant_variable
from main.model.adp.valuefunctions.features.futureBlockingContainers import future_blocking_containers
from main.model.adp.valuefunctions.features.futureBlockingStacks import future_blocking_stacks
from main.model.adp.valuefunctions.features.nonReachableContainers import non_reachable_containers
from main.model.adp.valuefunctions.features.nonReacheableStacks import non_reachable_stacks
from main.model.adp.valuefunctions.features.unorderedStacks import unordered_stacks
from main.model.dataclass.block import Block
from main.model.dataclass.stack import Stack
from main.model.dataclass.terminal import Terminal
from main.model.events.evaluatableEvents import EvaluatableEvents
from main.model.policies.adp import ADP
from main.util import sub_folder_file


class ADPSettings:
    DEFAULT_DISCOUNT_FACTOR = 1.0
    DEFAULT_INIT_WEIGHT = 1.0
    DEFAULT_DELTA = 0.9
    DEFAULT_EPSILON = 0.05
    DEFAULT_CONSTANT = 1.0
    DEFAULT_OPTIMIZED = False
    DEFAULT_CORRIDOR = -1
    DEFAULT_CORRIDOR_FEATURE = -1

    def __init__(self, discount_factor: float = DEFAULT_DISCOUNT_FACTOR,
                 init_weight: float = DEFAULT_INIT_WEIGHT,
                 delta: float = DEFAULT_DELTA,
                 epsilon: float = DEFAULT_EPSILON,
                 optimized: bool = DEFAULT_OPTIMIZED,
                 constant: float = DEFAULT_CONSTANT,
                 corridor: int = DEFAULT_CORRIDOR,
                 corridor_feature: int = DEFAULT_CORRIDOR_FEATURE):
        self.discount_factor = discount_factor
        self.init_weight = init_weight
        self.delta = delta
        self.epsilon = epsilon
        self.optimized = optimized
        self.constant = constant
        self.corridor = corridor
        self.corridor_feature = corridor_feature

    def get_name(self, base_name):
        discount = "-lambda{}".format(self.discount_factor) if self.discount_factor != ADPSettings.DEFAULT_DISCOUNT_FACTOR else ""
        weight = "-w{}".format(self.init_weight) if self.init_weight != ADPSettings.DEFAULT_INIT_WEIGHT else ""
        delta = "-d{}".format(self.delta) if self.delta != ADPSettings.DEFAULT_DELTA else ""
        epsilon = "-eps{}".format(self.epsilon) if self.epsilon != ADPSettings.DEFAULT_EPSILON else ""
        const = "-c{}".format(self.constant) if self.constant != ADPSettings.DEFAULT_CONSTANT else ""
        cor = "-cm{}".format(self.corridor) if self.corridor != ADPSettings.DEFAULT_CORRIDOR else ""
        corf = "-cmf{}".format(self.corridor_feature) if self.corridor_feature != ADPSettings.DEFAULT_CORRIDOR_FEATURE else ""
        opt = "-optimized" if self.optimized != ADPSettings.DEFAULT_OPTIMIZED else ""
        return "{}{}{}{}{}{}{}{}{}".format(base_name, discount, weight, delta, epsilon, const, cor, corf, opt)

available_algorithms = [
    "SingleFixed",
    "SingleHarmonic",
    "DoubleFixed",
    "DoubleHarmonic",
    "VFA1",
    "VFA2",
    "VFA3",
    "VFA4",
    "VFA5",
    "VFA6"
    ]

features_VFA1 = [
    blocking_containers,
    unordered_stacks,
    composite_measure,
    batch_label_difference,
    average_stack_height,
    non_reachable_stacks,
    non_reachable_containers,
    future_blocking_stacks,
    future_blocking_containers,
    constant
]

features_VFA2 = [
    blocking_containers,
    average_stack_height,
    non_reachable_stacks,
    future_blocking_stacks,
    constant
]

features_VFA3 = [
    composite_measure,
    batch_label_difference,
    non_reachable_stacks,
    future_blocking_containers,
    constant
]

features_VFA4 = [
    unordered_stacks,
    batch_label_difference,
    non_reachable_stacks,
    non_reachable_containers,
    constant
]

features_VFA5 = [
    blocking_containers,
    unordered_stacks,
    non_reachable_stacks,
    constant
]

#same as VFA3, but with adopted composite measure
features_VFA6 = [
    composite_adopted_measure,
    batch_label_difference,
    non_reachable_stacks,
    future_blocking_containers,
    constant
]

def init_terminal(terminal_type):
    if terminal_type == '1':
        return Terminal.empty_single_stack_block(7, 4)
    elif terminal_type == '2':
        return Terminal((
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True),
            Block((Stack(()), Stack(()), Stack(()), Stack(()), Stack(())), True)
        ), 4)
    # small, medium and big instances
    elif terminal_type == '3':
        return Terminal.empty_bay(50, 4)
    elif terminal_type == '4':
        return Terminal.empty_bay(100, 4)
    elif terminal_type == '5':
        return Terminal.empty_bay(200, 4)
    elif terminal_type == '6':
        return Terminal.empty_bay(20, 4)
    elif terminal_type == '7':
        return Terminal.empty_single_stack_block(15, 4)
    else:
        raise RuntimeError("Invalid Terminal type {} supplied".format(terminal_type))


def load_events(terminal_type):
    if terminal_type in ['1', '2']:
        return [EvaluatableEvents.load_evaluatable_events("20_12_25_250_{}".format(i)) for i in range(1, 17)]
    elif terminal_type == '3':
        return [EvaluatableEvents.load_evaluatable_events("40_15_250_250_{}".format(i)) for i in range(1, 17)]
    elif terminal_type == '4':
        return [EvaluatableEvents.load_evaluatable_events("40_15_500_250_{}".format(i)) for i in range(1, 17)]
    elif terminal_type == '5':
        return [EvaluatableEvents.load_evaluatable_events("40_15_1000_250_{}".format(i)) for i in range(1, 17)]
    elif terminal_type in ['6', '7']:
        return [EvaluatableEvents.load_evaluatable_events("40_15_100_250_{}".format(i)) for i in range(1, 17)]


def evaluate_adp(args) -> Tuple[List[float], List[float]]:
    """
    Function that evaluates a single event. A tuple is returned containing a list of all obtained values.
    :param alg_name:
    :param event:
    :return:
    """
    alg_name, event, instance_nr, terminal_type, number_sample_iterations, evaluation_samples, every_th_iteration, use_optimized, adp_settings = args
    print("{}:{} has been started".format(alg_name, instance_nr))
    initial_terminal = init_terminal(terminal_type)
    file_writer = FileWriter(alg_name, instance_nr, terminal_type, adp_settings)

    # adp settings
    discount_factor = adp_settings.discount_factor
    epsilon = adp_settings.epsilon
    if alg_name == "SingleFixed":
        single = True
        value_function_approx = AbstractState(Fixed(1, 0.05), AbstractState.underestimate)
    if alg_name == "SingleHarmonic":
        single = True
        value_function_approx = AbstractState(Harmonic(1, 0.05), AbstractState.underestimate)
    if alg_name == "DoubleFixed":
        single = False
        value_function_approx = AbstractState(Fixed(1, 0.05), AbstractState.underestimate)
    if alg_name == "DoubleHarmonic":
        single = False
        value_function_approx = AbstractState(Harmonic(1, 0.05), AbstractState.underestimate)
    # feature functions
    if alg_name.startswith("VFA"):
        single = False
        if alg_name == "VFA1":
            features = features_VFA1
        if alg_name == "VFA2":
            features = features_VFA2
        if alg_name == "VFA3":
            features = features_VFA3
        if alg_name == "VFA4":
            features = features_VFA4
        if alg_name == "VFA5":
            features = features_VFA5
        if alg_name == "VFA6":
            features = features_VFA6
        # replace constant with one that returns the value of the supplied constant
        # noinspection PyUnboundLocalVariable
        features[-1] = constant_variable(adp_settings.constant)

        # noinspection PyUnboundLocalVariable
        value_function_approx = BasisFunction(features, adp_settings.init_weight, delta=adp_settings.delta, file_writer=file_writer)

    # noinspection PyUnboundLocalVariable
    # container_dict = {1: 0, 2: 1} # key is container id, value is label. Label 0 means container may be placed
    # everywhere, other numbers need to match
    adp = ADP(event, initial_terminal, single, epsilon, value_function_approx, {}, number_sample_iterations,
              discount_factor, True, every_th_iteration, evaluation_samples, problem_instance=instance_nr,
              use_optimized_outcomes=use_optimized, corridor_size=adp_settings.corridor, corridor_feature=adp_settings.corridor_feature)

    iterations, reshuffles, init_values = extract_results(adp)

    # write instance result to instance file
    file_writer.write_to_instance_folder(FileWriter.FILE_INSTANCE_RESULTS, "iteration,{}".format(",".join(map(str, iterations))))
    file_writer.write_to_instance_folder(FileWriter.FILE_INSTANCE_RESULTS, "reshuffles,{}".format(",".join(map(str, reshuffles))))
    file_writer.write_to_instance_folder(FileWriter.FILE_INSTANCE_RESULTS, "initvalues,{}".format(",".join(map(str, init_values))))

    print("{}:{} has finished".format(alg_name, instance_nr))
    return reshuffles, init_values


def extract_results(adp: ADP):
    iterations = []
    reshuffles = []
    init_values = []
    for iteration in sorted(adp.evaluation_results):
        iterations.append(iteration)
        reshuffles.append(adp.evaluation_results[iteration][0])
        init_values.append(adp.evaluation_results[iteration][2])
    return iterations, reshuffles, init_values


def convert_result(results, iterations):
    avg_reshuffles = numpy.mean([tup[0] for tup in results], axis=0)
    avg_init_values = numpy.mean([tup[1] for tup in results], axis=0)

    s = "iteration,reshuffles,initvalues\n"
    for i in range(len(iterations)):
        s += "{},{},{}\n".format(iterations[i], avg_reshuffles[i], avg_init_values[i])

    return s



def main(alg_name: str, terminal_type: str, number_sample_iterations: int, evaluation_samples: int, every_th_iteration: int, use_optimized: bool, adp_settings: ADPSettings):
    events = load_events(terminal_type)

    with Pool(number_cores) as pool:
        job_args = [[alg_name, events[i], i+1, terminal_type, number_sample_iterations, evaluation_samples, every_th_iteration, use_optimized, adp_settings] for i in range(len(events))]

        result = pool.map(evaluate_adp, job_args)

        s = convert_result(result, [i for i in range(1, number_sample_iterations+1) if i%every_th_iteration==1])

        file = open(sub_folder_file(["evaluation", "final"], "t{}-{}.csv".format(terminal_type, adp_settings.get_name(alg_name))), "a+")
        file.write(s + "\n")
        file.close()

        pool.close()
        pool.join()


    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-N', default=151, help="Number of adp iterations")
    parser.add_argument('-e', default=150, help="Number of evaluation samples run")
    parser.add_argument('-i', default=10, help="Every ith iteration an evaluation is run")
    parser.add_argument('-c', '--cores', required=True, help="The size of the pool used. To maximize performance, give value equal to number of available cores", action="store")
    parser.add_argument('-a', '--algorithm', required=True, help="The algorithm that needs to be run", choices=available_algorithms)
    parser.add_argument('-t', '--terminal', required=True, action="store", help="Which terminal layout needs to be used. 1=gantry, 2=reachstacker", choices=['1','2','3','4','5','6', '7'])
    parser.add_argument('-o', '--optimized', default=False, action="store_true", help="Whether optimized outcomes needs to be used")


    parser.add_argument('-discount', default=ADPSettings.DEFAULT_DISCOUNT_FACTOR)
    parser.add_argument('-delta', default=ADPSettings.DEFAULT_DELTA)
    parser.add_argument('-weight', default=ADPSettings.DEFAULT_INIT_WEIGHT)
    parser.add_argument('-epsilon', default=ADPSettings.DEFAULT_EPSILON)
    parser.add_argument('-constant', default=ADPSettings.DEFAULT_CONSTANT)
    parser.add_argument('-corridor', default=ADPSettings.DEFAULT_CORRIDOR)
    parser.add_argument('-corridorf', default=ADPSettings.DEFAULT_CORRIDOR_FEATURE)



    args = parser.parse_args()

    number_cores = int(args.cores)
    alg_name = args.algorithm
    terminal_type = args.terminal
    N = int(args.N)
    evaluation_samples = int(args.e)
    every_th_iteration = int(args.i)
    optimized = args.optimized
    corridor = int(args.corridor)
    corridor_feature = int(args.corridorf)

    discount_factor = float(args.discount)
    init_weight = float(args.weight)
    delta = float(args.delta)
    epsilon = float(args.epsilon)
    constant = float(args.constant)

    # check if optimized flag is set when running the bigger problems (otherwise they wont terminate)
    assert optimized or int(terminal_type) <= 2

    adp_settings = ADPSettings(
        optimized=optimized,
        discount_factor=discount_factor,
        init_weight=init_weight,
        delta=delta,
        epsilon=epsilon,
        constant=constant,
        corridor=corridor,
        corridor_feature=corridor_feature
    )

    main(alg_name, terminal_type, N, evaluation_samples, every_th_iteration, optimized, adp_settings)


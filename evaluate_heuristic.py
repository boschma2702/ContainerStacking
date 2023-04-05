import argparse
from multiprocessing import Pool

import numpy

from evaluate_algorithm import load_events, init_terminal, ADPSettings
from main.model.adp.fileWriter import FileWriter
from main.model.policies.MMAdoptedRule import MMAdoptedRule
from main.model.policies.MMRule import MMRule
from main.model.policies.myopic import Myopic
from main.model.policies.policy import Policy
from main.util import sub_folder_file

available_algorithms = [
    "MyOpic",
    "MM",
    "MMAdopted"
    ]


class heuristicSetting(ADPSettings):

    def get_name(self, base_name):
        return base_name


def evaluate_policy(args):
    alg_name, event, instance_nr, terminal_type, evaluation_samples = args
    initial_terminal = init_terminal(terminal_type)
    container_labels = event.container_labels
    file_writer = FileWriter(alg_name, instance_nr, terminal_type, heuristicSetting())

    if alg_name == "MyOpic":
        policy: Policy = Myopic(event, initial_terminal, container_labels)
    if alg_name == "MM":
        policy: Policy = MMRule(event, initial_terminal, container_labels)
    if alg_name == "MMAdopted":
        policy: Policy = MMAdoptedRule(event, initial_terminal, container_labels)

    # noinspection PyUnboundLocalVariable
    mean, standard_dev = Policy.evaluate(policy, initial_terminal, event, evaluation_samples)
    file_writer.write_to_instance_folder(FileWriter.FILE_INSTANCE_RESULTS, "reshuffles,{}".format(mean))

    return mean


def convert_result(results, iterations):
    avg_mean = numpy.mean(results)

    s = "iteration,reshuffles\n"
    for i in range(len(iterations)):
        s += "{},{}\n".format(iterations[i], avg_mean)

    return s

def main(alg_name: str, terminal_type: str, evaluation_samples: int):
    # events = [EvaluatableEvents.load_evaluatable_events("20_12_30_250_{}".format(i)) for i in range(1, 17)]
    events = load_events(terminal_type)

    with Pool(number_cores) as pool:
        job_args = [[alg_name, events[i], i+1, terminal_type, evaluation_samples] for i in range(len(events))]
        # job_args = [[alg_name, events[i], i+1, terminal_type, number_sample_iterations, evaluation_samples, every_th_iteration] for i in [0, 1]]

        result = pool.map(evaluate_policy, job_args)

        s = convert_result(result, [i for i in range(1, evaluation_samples+2) if i%10==1])

        file = open(sub_folder_file(["evaluation", "final"], "t{}-{}.csv".format(terminal_type, alg_name)), "a+")
        file.write(s + "\n")
        file.close()

        pool.close()
        pool.join()


    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-e', default=150, help="Number of evaluation samples run")
    parser.add_argument('-c', '--cores', required=True, help="The size of the pool used. To maximize performance, give value equal to number of available cores", action="store")
    parser.add_argument('-a', '--algorithm', required=True, help="The algorithm that needs to be run", choices=available_algorithms)
    parser.add_argument('-t', '--terminal', required=True, action="store", help="Which terminal layout needs to be used. 1=gantry, 2=reachstacker", choices=['1','2','3','4','5','6','7','8'])

    args = parser.parse_args()

    number_cores = int(args.cores)
    alg_name = args.algorithm
    terminal_type = args.terminal
    evaluation_samples = int(args.e)

    # local dev settings
    # number_cores = 3
    # alg_name = "VFA2"
    # terminal_type = '1'
    # N = 11
    # evaluation_samples = 5
    # every_th_iteration = 2
    # evaluate_adp((alg_name, load_events()[0], 0, terminal_type, N, evaluation_samples, every_th_iteration))

    main(alg_name, terminal_type, evaluation_samples)

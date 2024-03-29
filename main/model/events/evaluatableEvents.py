from typing import Tuple, List

import json

from main.model.batch import RealizedBatch
from main.model.batch.batch import Batch
from main.model.events.events import Events
from main.model.events.generator import generate_events
from main.model.events.realizedEvents import RealizedEvents
from numpyencoder import NumpyEncoder

from main.util import writeToFile, sub_folder_file, sub_folder


class EvaluatableEvents(Events):

    def __init__(self, batches: Tuple[Batch], training_events: List[RealizedEvents], evaluating_events: List[RealizedEvents]):
        super().__init__(batches)
        self.sample_count_training = 0
        self.sample_count_evaluating = 0
        self.training_events = training_events
        self.evaluating_events = evaluating_events

    def sample(self) -> RealizedEvents:
        return self._get_training_sample()

    def sample_evaluating(self) -> RealizedEvents:
        return self._get_evaluating_sample()

    def reset(self):
        self.sample_count_training = 0
        self.sample_count_evaluating = 0

    def _get_training_sample(self) -> RealizedEvents:
        if self.sample_count_training == len(self.training_events):
            raise ValueError("Max training samples reached")
        self.sample_count_training += 1
        return self.training_events[self.sample_count_training - 1]

    def _get_evaluating_sample(self) -> RealizedEvents:
        if self.sample_count_evaluating == len(self.evaluating_events):
            raise ValueError("Max evaluating samples reached")
        self.sample_count_evaluating += 1
        return self.evaluating_events[self.sample_count_evaluating - 1]

    @classmethod
    def create_from_ids(cls, batches, nr_samples=1000):
        events = Events.create(batches)
        return cls(events.batches, [events.sample() for i in range(nr_samples)], [events.sample() for i in range(nr_samples)])

    @staticmethod
    def load_evaluatable_events(filename: str, extension="json", directory=sub_folder("events")):
        # directory = sub_folder_file("events", "{}.{}".format(filename, extension))
        direct = sub_folder_file(directory, "{}.{}".format(filename, extension))
        with open(direct) as json_file:
            data = json.load(json_file)
            ev: Tuple[Batch] = tuple([Batch(i%2==0, tuple([tuple(container) for container in data['events'][i]]))
                            for i in range(len(data['events']))])
            training_events: List[RealizedEvents, ...] = [
                RealizedEvents(
                    tuple([RealizedBatch(i%2==0, EvaluatableEvents.list_to_tuple_of_containers(sample[i])) for i in range(len(sample))])
                )
                for sample in data['training_events']
            ]
            evaluating_events: List[RealizedEvents, ...] = [
                RealizedEvents(
                    tuple([RealizedBatch(i % 2 == 0, EvaluatableEvents.list_to_tuple_of_containers(sample[i])) for i in
                           range(len(sample))])
                )
                for sample in data['evaluating_events']
            ]
            return EvaluatableEvents(ev, training_events, evaluating_events)


    @staticmethod
    def list_to_tuple_of_containers(list_of_containers):
        return tuple([tuple(container) for container in list_of_containers])

    def write_evaluatable_events(self, filename: str, directory=sub_folder("events")):
        d = {
            "events": EvaluatableEvents.convert_events_to_lists(self.batches),
            "training_events": [EvaluatableEvents.convert_events_to_lists(training_event.batches) for training_event in self.training_events],
            "evaluating_events": [EvaluatableEvents.convert_events_to_lists(evaluating_event.batches) for evaluating_event in self.evaluating_events]
        }
        writeToFile(filename, json.dumps(d, cls=NumpyEncoder), extension="json", base_path=directory)

    @staticmethod
    def convert_events_to_lists(batches):
        return [[list(container) for container in batch.containers] for batch in batches]

    @classmethod
    def create_evaluatable_batches(cls, period_slots, dwell_time, number_of_containers, nr_samples=1000):
        events = generate_events(period_slots, dwell_time, number_of_containers)
        training_events = [events.sample() for i in range(nr_samples)]
        evaluating_events = [events.sample() for i in range(nr_samples)]
        return cls(events.batches, training_events, evaluating_events)


# events = EvaluatableEvents.create_evaluatable_batches(8,3,10)
# print(EvaluatableEvents.load_evaluatable_events("test"))
# writeToFile("test", events.write_evaluatable_events(), extension="json")

# first = events.sample()
# print(first)
# print(events.sample())
# print(events.sample())
# events.reset()
# print(first == events.sample())

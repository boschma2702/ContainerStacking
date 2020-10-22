from typing import List

import numpy

from main.model.batch.batch import Batch
from main.model.dataclass import Container
from main.model.events.events import Events


def generate_events(period_slots: int, expected_dwell_periods, nr_containers) -> Events:
    """
    Generates a random Events. Generation is done as follows. First an arrival period is sampled for all containers.
    This sampling is done uniform over the number of period slots. After that, for each container a dwell time is sampled
    from a exponential distribution with the given expected value. This yields a period slot when the container departs.
    Containers with the same arrival and departure slots are then grouped into batches and a Events object is created.

    :param period_slots:
    :param expected_dwell_periods:
    :param nr_containers:
    :return:
    """

    batches: List[List[Container], ...] = [[] for e in range(period_slots*2)]

    inbound_batches = numpy.random.randint(period_slots, size=nr_containers)
    outbound_batches = [int(i) for i in
                        numpy.random.exponential(expected_dwell_periods, size=nr_containers).round()]

    for i in range(nr_containers):
        inbound_label = inbound_batches[i]
        outbound_label = inbound_label + outbound_batches[i]

        container: Container = (i, outbound_label, -1)

        inbound_index = inbound_label * 2
        outbound_index = outbound_label * 2 + 1

        batches[inbound_index].append(container)
        # only add if it is within the planning period
        if outbound_label < period_slots:
            batches[outbound_index].append(container)

    return Events(tuple([Batch(i % 2 == 0, tuple(batches[i])) for i in range(len(batches))]))


# # events = generate_events(10, 2, 100)
# # events = Events.create([(1,2), (1,), (3,4,5), (2,3,4)])
# events = Events.create([(1,2), (), (3,4), (2,3)])
# # init_terminal = ImmutableTerminal.empty(20, 4)
# init_terminal = ImmutableTerminal.empty(3, 4)
# leveling = LevelingHeuristic(events, init_terminal)
# leveling.evaluate()
# pbfs = PBFS(events, init_terminal)
# pbfs.evaluate()

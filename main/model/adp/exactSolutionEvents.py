from evaluate_algorithm import init_terminal, load_events
from main.model.policies.pbfs import PBFS
from main.model.policies.policy import Policy

events = load_events('1')

t = init_terminal('1')

for i in range(len(events)):
    index = i+1
    print("handling {}".format(index))
    event = events[i]
    pbfs = PBFS(event, t)
    mean, std = Policy.evaluate(pbfs, t, event, nr_samples=150)
    print("{}: mean: {} std: {}".format(i+1, mean, std))


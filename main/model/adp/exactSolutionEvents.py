from evaluate_algorithm import init_terminal
from main.model.events.evaluatableEvents import EvaluatableEvents
from main.model.policies.pbfs import PBFS
from main.model.policies.policy import Policy

events = [EvaluatableEvents.load_evaluatable_events("20_12_25_250_{}".format(i)) for i in range(1, 17)]

t = init_terminal('2')

index = 1

print("handling {}".format(index))
event = EvaluatableEvents.load_evaluatable_events("20_12_25_250_{}".format(index))
pbfs = PBFS(event, t)
mean, std = Policy.evaluate(pbfs, t, event, nr_samples=150)
print("{}: mean: {} std: {}".format(index, mean, std))


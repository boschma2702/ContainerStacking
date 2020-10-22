class StepSize:
    alpha: float

    def update_alpha(self, iteration: int):
        raise NotImplementedError("Not implemented")

    def get_alpha(self):
        return self.alpha


class Fixed(StepSize):
    """
    Constant step size. Alpha decreases at a constant rate with the given step size. Alpha can not drop lower than the
    given step size.
    """
    def __init__(self, init_alpha, step_size: float):
        self.alpha = init_alpha
        self.step_size = step_size

    def update_alpha(self, iteration: int):
        self.alpha = max(self.step_size, self.alpha - self.step_size)


class Harmonic(StepSize):
    """
    Harmonic step size. This is a generalization of the 1/n rule. An increased a, decreases the rate at which the step
    size drops to zero. Values of a can differ immense. For instance 5 may be sufficient or 1000. Powell suggest to pick
    an a, such that the alpha equals to .05 at point of convergence. To overcome that at big iterations, no new
    information is learned, the step size will not drop below the given minimium value.
    """
    def __init__(self, lambda_value, min_alpha):
        self.lambda_value = lambda_value
        self.min_alpha = min_alpha
        self.alpha = 1

    def update_alpha(self, iteration: int):
        self.alpha = max(self.lambda_value / (self.lambda_value + iteration - 1), self.min_alpha)


class Season:
    """Class that keeps track when the season ends"""

    def __init__(self, DISCRETE_GENERATIONS):
        self.countdown = float("inf")
        self.DISCRETE_GENERATIONS = DISCRETE_GENERATIONS
        self.reset()

    def reset(self):
        """Reset the season length tracker"""
        self.countdown = (
            self.DISCRETE_GENERATIONS if self.DISCRETE_GENERATIONS else float("inf")
        )

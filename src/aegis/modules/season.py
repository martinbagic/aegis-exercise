class Season:
    """Class that keeps track when the season ends"""

    def __init__(self, DISCRETE_GENERATIONS):
        self.countdown = DISCRETE_GENERATIONS if DISCRETE_GENERATIONS else float("inf")
        self.DISCRETE_GENERATIONS = DISCRETE_GENERATIONS

    def reset(self):
        """Reset the season length tracker"""
        self.countdown += self.DISCRETE_GENERATIONS

class Trait:
    """Genetic trait"""

    legal = ("surv", "repr", "neut", "muta")

    def __init__(self, name, params):
        def get(key):
            return params[f"G_{name}_{key}"]

        self.evolvable = get("evolvable")
        self.initial = get("initial")
        self.name = name

        if self.evolvable:
            self.agespecific = get("agespecific")
            self.interpreter = get("interpreter")
            self.lo = get("lo")
            self.hi = get("hi")

            # Number of loci needed to encode this trait is 1 if the trait is not evolvable
            #   and MAX_LIFESPAN if it is evolvable
            self.length = params["MAX_LIFESPAN"] if self.agespecific else 1

        else:
            self.length = 0

        self.validate()

    def validate(self):
        assert isinstance(self.evolvable, bool)
        assert 0 <= self.initial <= 1

        if self.evolvable:
            assert isinstance(self.agespecific, bool)
            assert self.interpreter in (
                "uniform",
                "exp",
                "binary",
                "binary_exp",
                "binary_switch",
                "switch",
            )
            assert 0 <= self.lo <= 1
            assert 0 <= self.hi <= 1

    def __len__(self):
        return self.length

    def __str__(self):
        return self.name

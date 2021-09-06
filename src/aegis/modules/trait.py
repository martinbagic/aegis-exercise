class Trait:
    """Genetic trait"""

    legal = ("surv", "repr", "neut", "muta")

    def __init__(self, name, params, start):
        def get(key):
            return params[f"G_{name}_{key}"]

        self.name = name

        # Attributes set by the configuration files
        self.evolvable = get("evolvable")
        self.agespecific = get("agespecific")
        self.interpreter = get("interpreter")
        self.lo = get("lo")
        self.hi = get("hi")
        self.initial = get("initial")

        # Determine the number of loci encoding the trait
        if self.evolvable:
            if self.agespecific:  # one locus per age
                self.length = params["MAX_LIFESPAN"]
            else:  # one locus for all ages
                self.length = 1
        else:  # no loci for a constant trait
            self.length = 0

        self._validate()

        # Set positions in the genome
        self.start = start
        self.end = self.start + self.length
        self.slice = slice(self.start, self.end)

    def _validate(self):
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

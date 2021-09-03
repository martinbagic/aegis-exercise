class Gstruc:
    """Genome structure"""

    def __init__(self, params):

        self.traits = {name: Trait(name, params) for name in Trait.legal}
        self.evolvable = [trait for trait in self.traits.values() if trait.evolvable]
        self.length = 0

        for trait in self.traits.values():
            trait.start = self.length
            trait.end = self.length + trait.length
            trait.slice = slice(trait.start, trait.end)

            self.length = trait.end

    def __getitem__(self, name):
        return self.traits[name]

    def __len__(self):
        return self.length


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
            self.agespec = get("agespec")
            self.interpreter = get("interpreter")
            self.lo = get("lo")
            self.hi = get("hi")

            # Number of loci needed to encode this trait is 1 if the trait is not evolvable
            #   and MAX_LIFESPAN if it is evolvable
            self.length = params["MAX_LIFESPAN"] if self.agespec else 1

        else:
            self.length = 0

        self.validate()

    def validate(self):
        assert isinstance(self.evolvable, bool)
        assert 0 <= self.initial <= 1

        if self.evolvable:
            assert isinstance(self.agespec, bool)
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

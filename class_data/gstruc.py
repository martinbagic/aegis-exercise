class Gstruc:
    """Genome structure"""

    def __init__(self, traits):

        self.traits = {}
        self.evolvable = []
        self.length = 0

        for trait in traits:
            trait.start = self.length
            trait.end = self.length + trait.length
            trait.slice = slice(trait.start, trait.end)

            self.length = trait.end
            self.traits[trait.name] = trait
            if trait.evolvable:
                self.evolvable.append(trait)

    def __getattr__(self, name):
        return self.traits[name]

    def __getitem__(self, name):
        return self.traits[name]

    def __len__(self):
        return self.length


class Trait:
    """Genetic trait"""

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

            self.length = (
                params["MAX_LIFESPAN"] if self.agespec else 1
            )  # Number of loci needed to encode this trait is 1 if the trait is not evolvable and MAX_LIFESPAN if it is evolvable

        else:
            self.length = 0

    def __len__(self):
        return self.length

    def cut(self, array):
        """Return the loci of each individual that encode this trait"""
        return array[:, self.start : self.end]

    def __str__(self):
        return self.name

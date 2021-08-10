from aegis import PAN


class Gstruc:
    """Genome structure"""

    def __init__(self, params):

        self.traits = {name: Trait(name, params) for name in PAN.traits}
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

    def __str__(self):
        return self.name

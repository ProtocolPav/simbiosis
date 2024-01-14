import random
from logs import log


class Gene:
    def __init__(self, name: str, acronym: str, value: float, can_mutate: bool = True,
                 min_value: float = 0, max_value: float = 99999, integer: bool = False):
        self.name = name
        self.acronym = acronym.upper()
        self.value = value
        self.can_mutate = can_mutate
        self.min = min_value
        self.max = max_value
        self.is_type_integer = integer

    def mutate(self, probability: float = 0.2, factor: float = 1):
        if self.can_mutate:
            old_value = self.value

            if random.choices(population=["mutate", "no mutate"], weights=[probability, 1-probability])[0] == "mutate":
                if self.is_type_integer:
                    self.value += round(random.uniform(-2*factor, 2*factor))
                else:
                    self.value += random.uniform(-0.2*factor, 0.2*factor)

                if self.value < self.min:
                    self.value = self.min
                if self.value > self.max:
                    self.value = self.max

            if old_value == self.value:
                log(f"[MUTATION] {self.name} No Change")
            else:
                log(f"[MUTATION] {self.name} ({old_value} -> {self.value})")


class CreatureGenes:
    def __init__(self, species: int, generation: int):
        # Genes affecting Creature Appearance (Phenotype)
        self.colour_red = Gene(name="Red Colour", acronym="CLR", value=random.randint(0, 255),
                               min_value=0, max_value=255, integer=True)
        self.colour_green = Gene(name="Green Colour", acronym="CLG", value=random.randint(0, 255),
                                 min_value=0, max_value=255, integer=True)
        self.colour_blue = Gene(name="Blue Colour", acronym="CLB", value=random.randint(0, 255),
                                min_value=0, max_value=255, integer=True)
        self.radius = Gene(name="Creature Radius Size", acronym="SIZ", value=random.uniform(0.5, 7),
                           min_value=0.5)

        # Genes affecting Creature movement
        self.speed = Gene(name="Speed", acronym="SPD", value=random.uniform(0, 50),
                          min_value=0)

        # Genes affecting the Creature's Energy Consumption
        self.base_energy = Gene(name="Energy Consumed per Second", acronym="ENB", value=random.uniform(1, 100),
                                min_value=1)
        self.movement_energy = Gene(name="Energy Consumed for Movement", acronym="ENM", value=random.uniform(5, 100),
                                    min_value=1)
        self.turning_energy = Gene(name="Energy Consumed for Turning", acronym="ENT", value=random.uniform(5, 100),
                                   min_value=1)
        self.birth_energy = Gene(name="Energy Consumed for Birthing", acronym="ENI",
                                 value=random.uniform(self.base_energy.value * 60, self.base_energy.value * 6000),
                                 min_value=1)
        self.plant_energy = Gene(name="% of Energy Gained From Eating", acronym="ENP", value=random.random(),
                                 min_value=0)

        # Genes affecting Creature Behaviour
        self.vision_radius = Gene(name="Vision Radius", acronym="VIR",
                                  value=random.uniform(self.radius.value, self.radius.value + 10))
        self.vision_angle = Gene(name="Vision Angle", acronym="VIA", value=random.randint(1, 180),
                                 min_value=1)
        self.react_towards = Gene(name="Reaction Towards Entity", acronym="RTO", value=random.random(),
                                  min_value=0)
        self.react_speed = Gene(name="Reaction Speed", acronym="RSP", value=random.uniform(1, 13),
                                min_value=0)

        # Genes which offset the RTO based on what the creature is seeing
        # Currently does nothing
        self.food_offset = Gene(name="Reaction Food Offset", acronym="RFO", value=random.uniform(-0.5, 0.5),
                                min_value=-0.5, max_value=0.5)
        self.stranger_offset = Gene(name="Reaction Stranger Offset", acronym="RSO", value=random.uniform(-0.5, 0.5),
                                    min_value=-0.5, max_value=0.5)
        self.known_offset = Gene(name="Reaction Known Offset", acronym="RKO", value=random.uniform(-0.5, 0.5),
                                 min_value=-0.5, max_value=0.5)

        # Data Genes (No mutation, affects Data)
        self.species = Gene(name="Species", acronym="SPE", value=species, can_mutate=False)
        self.generation = Gene(name="Generation", acronym="GEN", value=generation, can_mutate=False)

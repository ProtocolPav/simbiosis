import random
from logs import log


class Gene:
    def __init__(self, name: str, acronym: str, value: float, can_mutate: bool = True,
                 min_value: float = None, max_value: float = None):
        self.name = name
        self.acronym = acronym.upper()
        self.value = value
        self.can_mutate = can_mutate
        self.min = min_value
        self.max = max_value

    def mutate(self):
        if self.can_mutate:
            old_value = self.value

            if random.choices(population=["mutate", "no mutate"], weights=[50, 250])[0] == "mutate":
                if self.acronym in ['CLR', 'CLB', 'CLG']:
                    self.value += random.randint(2, 2)
                    if self.value < 0:
                        self.value = 10
                    elif self.value > 255:
                        self.value = 245
                else:
                    self.value += random.uniform(-0.2, 0.2)

                if self.acronym in ['CLH', 'RTL', 'RTR', 'RTB', 'RTW', 'RAW', 'RBO', 'RTF', 'RAF', 'RLF', 'RRF', 'RBF']:
                    if self.value < 0:
                        self.value = abs(self.value)
                    elif self.value > 1:
                        self.value -= 1

            if old_value == self.value:
                log(f"[MUTATION] {self.name} No Change")
            else:
                log(f"[MUTATION] {self.name} ({old_value} -> {self.value})")


class CreatureGenes:
    def __init__(self, species: int, generation: int):
        # Genes affecting Creature Appearance (Phenotype)
        self.colour_red = Gene(name="Red Colour", acronym="CLR", value=random.randint(0, 255))
        self.colour_green = Gene(name="Green Colour", acronym="CLG", value=random.randint(0, 255))
        self.colour_blue = Gene(name="Blue Colour", acronym="CLB", value=random.randint(0, 255))
        self.radius = Gene(name="Creature Radius Size", acronym="SIZ", value=random.uniform(0.5, 7))

        # Genes affecting Creature movement
        self.speed = Gene(name="Speed", acronym="SPD", value=random.uniform(0, 50))

        # Genes affecting the Creature's Energy Consumption
        self.base_energy = Gene(name="Energy Consumed per Second", acronym="ENB", value=random.uniform(1, 100))
        self.movement_energy = Gene(name="Energy Consumed for Movement", acronym="ENM", value=random.uniform(5, 100))
        self.turning_energy = Gene(name="Energy Consumed for Turning", acronym="ENT", value=random.uniform(5, 100))
        self.birth_energy = Gene(name="Energy Consumed for Birthing", acronym="ENI",
                                 value=random.uniform(self.base_energy.value * 60, self.base_energy.value * 6000))
        self.plant_energy = Gene(name="% of Energy Gained From Eating", acronym="ENP", value=random.random())

        # Genes affecting Creature Behaviour
        self.vision_radius = Gene(name="Vision Radius", acronym="VIR", value=random.uniform(self.radius.value, self.radius.value+10))
        self.vision_angle = Gene(name="Vision Angle", acronym="VIA", value=random.randint(1, 180))
        self.react_towards = Gene(name="Reaction Towards Entity", acronym="RTO", value=random.random())
        self.react_away = Gene(name="Reaction Away from Entity", acronym="RAW", value=1-self.react_towards.value)
        self.react_speed = Gene(name="Reaction Speed", acronym="RSP", value=random.randint(1, 13))

        # Data Genes (No mutation, affects Data)
        self.species = Gene(name="Species", acronym="SPE", value=species, can_mutate=False)
        self.generation = Gene(name="Generation", acronym="GEN", value=generation, can_mutate=False)

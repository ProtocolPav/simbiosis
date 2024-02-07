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

            if random.choices(population=["mutate", "no mutate"], weights=[probability, 1 - probability])[0] == "mutate":
                if self.is_type_integer:
                    self.value += round(random.uniform(-2 * factor, 2 * factor))
                else:
                    self.value += random.uniform(-0.2 * factor, 0.2 * factor)

                if self.value < self.min:
                    self.value = self.min
                if self.value > self.max:
                    self.value = self.max

            if old_value == self.value:
                log(f"[MUTATION] {self.name} No Change")
            else:
                log(f"[MUTATION] {self.name} ({old_value} -> {self.value})")

    def save_gene(self, variable_name: str) -> dict:
        return {'attr': variable_name,
                'name': self.name,
                'acronym': self.acronym,
                'value': self.value,
                'can_mutate': self.can_mutate,
                'min': self.min,
                'max': self.max,
                'is_integer': self.is_type_integer}


class CreatureGenes:
    # Genes affecting Creature Appearance (Phenotype)
    colour_red: Gene
    colour_green: Gene
    colour_blue: Gene
    radius: Gene

    # Genes affecting Creature movement
    speed: Gene

    # Genes affecting the Creature's Energy Consumption
    base_energy: Gene
    movement_energy: Gene
    turning_energy: Gene
    birth_energy: Gene
    plant_energy: Gene

    # Genes affecting Creature Behaviour
    vision_radius: Gene
    vision_angle: Gene
    react_towards: Gene
    react_speed: Gene

    # Genes which offset the RTO based on what the creature is seeing
    food_offset: Gene
    stranger_offset: Gene
    known_offset: Gene

    # Data Genes (No mutation, affects Data)
    species: Gene
    generation: Gene

    def __init__(self, genes_list: list[dict]):
        """
        Iterates over the gene_list given. This is a list of dictionaries, which is present in the save files.
        :param genes_list:
        """
        for gene in genes_list:
            self.__setattr__(gene['attr'],
                             Gene(gene['name'], gene['acronym'], gene['value'], gene['can_mutate'], gene['min'], gene['max'],
                                  gene['is_integer']))

    @classmethod
    def load(cls, genes_list: list[dict]):
        return cls(genes_list)

    @classmethod
    def create(cls, species: int, generation: int):
        genes_object = cls([])

        # Genes affecting Creature Appearance (Phenotype)
        genes_object.colour_red = Gene(name="Red Colour", acronym="CLR", value=random.randint(0, 255),
                                       min_value=0, max_value=255, integer=True)
        genes_object.colour_green = Gene(name="Green Colour", acronym="CLG", value=random.randint(0, 255),
                                         min_value=0, max_value=255, integer=True)
        genes_object.colour_blue = Gene(name="Blue Colour", acronym="CLB", value=random.randint(0, 255),
                                        min_value=0, max_value=255, integer=True)
        genes_object.radius = Gene(name="Creature Radius Size", acronym="SIZ", value=random.uniform(0.5, 7),
                                   min_value=0.5)

        # Genes affecting Creature movement
        genes_object.speed = Gene(name="Speed", acronym="SPD", value=random.uniform(0, 50),
                                  min_value=0)

        # Genes affecting the Creature's Energy Consumption
        genes_object.base_energy = Gene(name="Energy Consumed per Second", acronym="ENB", value=random.uniform(1, 100),
                                        min_value=1)
        genes_object.movement_energy = Gene(name="Energy Consumed for Movement", acronym="ENM", value=random.uniform(5, 100),
                                            min_value=1)
        genes_object.turning_energy = Gene(name="Energy Consumed for Turning", acronym="ENT", value=random.uniform(5, 100),
                                           min_value=1)
        genes_object.birth_energy = Gene(name="Energy Consumed for Birthing", acronym="ENI",
                                         value=random.uniform(genes_object.base_energy.value * 60,
                                                              genes_object.base_energy.value * 6000),
                                         min_value=1)
        genes_object.plant_energy = Gene(name="% of Energy Gained From Eating", acronym="ENP", value=random.random(),
                                         min_value=0)

        # Genes affecting Creature Behaviour
        genes_object.vision_radius = Gene(name="Vision Radius", acronym="VIR",
                                          value=random.uniform(genes_object.radius.value, genes_object.radius.value + 10))
        genes_object.vision_angle = Gene(name="Vision Angle", acronym="VIA", value=random.randint(1, 180),
                                         min_value=1)
        genes_object.react_towards = Gene(name="Reaction Towards Entity", acronym="RTO", value=random.random(),
                                          min_value=0)
        genes_object.react_speed = Gene(name="Reaction Speed", acronym="RSP", value=random.uniform(1, 13),
                                        min_value=0)

        # Genes which offset the RTO based on what the creature is seeing
        genes_object.food_offset = Gene(name="Reaction Food Offset", acronym="RFO", value=random.uniform(-0.5, 0.5),
                                        min_value=-0.5, max_value=0.5)
        genes_object.stranger_offset = Gene(name="Reaction Stranger Offset", acronym="RSO", value=random.uniform(-0.5, 0.5),
                                            min_value=-0.5, max_value=0.5)
        genes_object.known_offset = Gene(name="Reaction Known Offset", acronym="RKO", value=random.uniform(-0.5, 0.5),
                                         min_value=-0.5, max_value=0.5)

        # Data Genes (No mutation, affects Data)
        genes_object.species = Gene(name="Species", acronym="SPE", value=species, can_mutate=False)
        genes_object.generation = Gene(name="Generation", acronym="GEN", value=generation, can_mutate=False)

        return genes_object

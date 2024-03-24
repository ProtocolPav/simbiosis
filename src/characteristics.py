from src.entity import Creature


def generate_characteristics(check_creature: Creature, creatures_list: list[Creature]):
    genes = [creature.genes for creature in creatures_list]

    characteristics_dict = {}
    # Speed Characteristic
    speed_data = [gene.speed.value for gene in genes]
    speed_data.sort()
    q1 = speed_data[len(speed_data)//4]
    q3 = speed_data[3 * len(speed_data)//4]

    if check_creature.genes.speed.value <= q1:
        characteristics_dict['speed'] = 'Slow'
    elif check_creature.genes.speed.value >= q3:
        characteristics_dict['speed'] = 'Fast'
    else:
        characteristics_dict['speed'] = 'Average'

    # Accuracy
    reaction_speed_data = [gene.react_speed.value / gene.speed.value for gene in genes]
    reaction_speed_data.sort()
    q1 = 4
    q3 = 100

    if q1 <= check_creature.genes.react_speed.value / check_creature.genes.speed.value <= q3:
        characteristics_dict['accuracy'] = f'Accurate {check_creature.genes.react_speed.value / check_creature.genes.speed.value}'
    else:
        characteristics_dict['accuracy'] = f'Inaccurate {check_creature.genes.react_speed.value / check_creature.genes.speed.value}'

    print(characteristics_dict)

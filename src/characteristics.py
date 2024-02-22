from src.genes import CreatureGenes


class Characteristics:
    def __init__(self, genes: list[CreatureGenes]):
        self.genes = genes

    def add_gene(self, gene: CreatureGenes):
        self.genes.append(gene)

    def generate_characteristics(self, creature_genes: CreatureGenes):
        characteristics_dict = {}
        # Speed Characteristic
        speed_data = [gene.speed.value for gene in self.genes]
        speed_data.sort()
        q1 = speed_data[len(speed_data)//4]
        q3 = speed_data[3 * len(speed_data)//4]

        if creature_genes.speed.value <= q1:
            characteristics_dict['speed'] = 'Slow'
        elif creature_genes.speed.value >= q3:
            characteristics_dict['speed'] = 'Fast'
        else:
            characteristics_dict['speed'] = 'Average'

        # Accuracy
        reaction_speed_data = [gene.react_speed for gene in self.genes]
        reaction_speed_data.sort()
        q1 = reaction_speed_data[len(reaction_speed_data)//4]
        q3 = reaction_speed_data[3 * len(reaction_speed_data)//4]


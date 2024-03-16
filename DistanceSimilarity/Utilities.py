import math


def convert_to_ontology(b1, b2):
    ontology = {}
    
    # get all triples with b1 and b2
    triples = df[((df['Subject'] == b1) | (df['Subject'] == b2)) & (df['Predicate'] != 'alternative brand')]
    

    for _, row in triples.iterrows():
        subject = row['Subject']
        predicate = row['Predicate']
        obj = row['Object']

        # Initialize ontology entry
        if subject not in ontology:
            ontology[subject] = {'ancestors': [], 'associations': []}

        # Process different predicates
        if predicate == 'generic name is':
            ontology[subject]['ancestors'].append(obj)
        else:
            ontology[subject]['associations'].append(obj)

    return ontology


def PCA_Score(brand1, brand2, ontology):
    
    common_ancestors = len(set(ontology[brand1]['ancestors']).intersection(ontology[brand2]['ancestors']))
    total_ancestors = len(set(ontology[brand1]['ancestors']).union(ontology[brand2]['ancestors']))
    pca_score = common_ancestors / total_ancestors
    
    return pca_score
    
def PCAS_Score(brand1, brand2, ontology):
    
    common_associations = len(set(ontology[brand1]['associations']).intersection(ontology[brand2]['associations']))
    total_associations = len(set(ontology[brand1]['associations']).union(ontology[brand2]['associations']))
    pcas_score = common_associations / total_associations
    
    return pcas_score

def PBAS_Score(entity1, entity2, ontology):

    binding_associations = len(set(ontology[entity1]['associations']).intersection(ontology[entity2]['associations']))
    total_associations = len(set(ontology[entity1]['associations']).union(ontology[entity2]['associations']))

    pbas_score = binding_associations / total_associations

    return pbas_score


def calculate_similarity(b1, b2, f_ca=0.5, f_cas=0.5):
    # Retrieve ontology of b1 and b2
    ontology = convert_to_ontology(b1, b2)
    
    # Calculate PCA
    pca = PCA_Score(b1, b2, ontology)
    
    # Calculate PCAS
    pcas = PCAS_Score(b1, b2, ontology)
    
    # Similarity score using weighted sum
    similarity_score = f_ca * pca + f_cas * pcas
    
    return similarity_score


def calculate_distance(b1, b2, w_ca=1.0, w_cas=1.0, w_ab=1.0):
    # Retrieve ontology of b1 and b2
    ontology = convert_to_ontology(b1, b2)
    
    # Calculate PCA
    pca = PCA_Score(b1, b2, ontology)

    # Calculate PCAS
    pcas = PCAS_Score(b1, b2, ontology)

    # Calculate PBAS
    pbas = PBAS_Score(b1, b2, ontology)
    
    # Apply logarithmic transformation and weights
    distance = 0
    if pca != 0:
        distance += w_ca * math.log(1 / pca)
    if pcas != 0:
        distance += w_cas * math.log(1 / pcas)
    distance += w_ab * pbas
    
    return distance



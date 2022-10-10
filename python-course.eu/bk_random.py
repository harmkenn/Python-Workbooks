""" 
This module provides functions to draw weighted samples from a population
"""

import random
import numpy as np

def find_interval(x, 
                  partition, 
                  endpoints=True):
    """ find_interval -> i
        If endpoints is True, "i" will be the index for which applies
        partition[i] < x < partition[i+1], if such an index exists.
        -1 otherwise
        
        If endpoints is False, "i" will be the smallest index 
        for which applies x < partition[i]. If no such index exists 
        "i" will be set to len(partition)
    """
    for i in range(0, len(partition)):
        if x < partition[i]:
            return i-1 if endpoints else i
    return -1 if endpoints else len(partition)


def weighted_choice(sequence, weights):
    """ 
    weighted_choice selects a random element of 
    the sequence according to the list of weights
    """
    x = np.random.random()
    cum_weights = [0] + list(np.cumsum(weights))
    index = find_interval(x, cum_weights)
    return sequence[index]

def cartesian_choice(*iterables):
    """
    A list with random choices from each iterable of iterables 
    is being created in respective order.
    
    The result list can be seen as an element of the 
    Cartesian product of the iterables 
    """
    res = []
    for population in iterables:
        res.append(random.choice(population))
    return res



def weighted_cartesian_choice(*iterables):
    """
    A list with weighted random choices from each iterable of iterables 
    is being created in respective order
    """
    res = []
    for population, weights in iterables:
        lst = weighted_choice(population, weights)
        res.append(lst)
    return res


def weighted_sample(population, weights, k):
    """ 
    This function draws a random sample of length k 
    from the sequence 'population' according to the 
    list of weights
    """
    sample = set()
    population = list(population)
    weights = list(weights)
    while len(sample) < k:
        choice = weighted_sample(population, weights)
        sample.add(choice)
        index = population.index(choice)
        weights.pop(index)
        population.remove(choice)
        weights = [ x / sum(weights) for x in weights]
    return list(sample)


def weighted_sample_alternative(population, weights, k):
    """ 
    Alternative way to previous implementation.

    This function draws a random sample of length k 
    from the sequence 'population' according to the 
    list of weights
    """
    sample = set()
    population = list(population)
    weights = list(weights)
    while len(sample) < k:
        choice = weighted_sample(population, weights)
        if choice not in sample:
            sample.add(choice)
    return list(sample)





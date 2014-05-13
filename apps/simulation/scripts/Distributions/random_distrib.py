"""
Distribution module, given an array (vector) of probabilities
(independent or accumulated) returns n (samples) on a dictionary
 """

import random

# ====================================================================
def List_to_hist(input_list):
    """
    @return : dict-like histogram of a list/vector passd in
    
    """
    hist = {}
    for x in input_list:
        if x in hist:
            hist[x] += 1
        else:
            hist[x] = 1
    return hist

# =====================================================================
def Nice_hist_print(hist):
    """
    prints a dictionary in the format: a - b
    """
    for key in hist:
        print key,
        print " - ",
        print hist[key]
        

# =====================================================================
""" Accmulated probability in vector
input example: [20, 40, 70, 100]
                ^   ^   ^    ^
                |   |   |    |
return:        0:2 1:3 2:7  3:4
"""
def Cumulative_vec_samples(vector, samples):
    """
    @param vector: vector of accumulated probabilities
    @param samples: number of simulations
    @return : a sorted list of events by index
    """
    res = []
    
    for x in xrange(samples):
        rand = random.uniform(0,100)
        prev = 0
        count = 0

        for hour in vector:
            if rand > prev and rand < hour:
                res.append(count)
    
            count += 1
            prev = hour

    return sorted(res)

# Polymorfism of the same function, last version
def Cumulative_vec_distr(distrib):
    """
    @param distrib: vector of tuples of accumulated probabilities
    @return : integer
    """
    rand = random.randint(0,100)

    for i in xrange(len(distrib)):
        if distrib[i][1] >= rand:
            interval_bot = distrib[i][0][0]
            interval_top = distrib[i][0][1]
            final = random.randint(interval_bot,interval_top)
            break

    return final

# ======================================================================
""" Probability for single item
input example: [0.2, 0.2, 0.3, 0.3]
                 ^    ^    ^    ^
                 |    |    |    |
return:         0:2  1:3  2:7  3:4
"""
def Non_cumulative_vec_distr(vector, samples):
    """
    @param vector: vector of accumulated probabilities
    @param samples: number of simulations
    @return : a sorted list of events by index
    """
    res = []

    for t in xrange(samples):
        rand = random.uniform(0,1)

        count = 0
        suma = 0
        for x in vector:
            suma += x
            if suma >= rand:
                res.append(count)
                break
        
            count += 1

    return sorted(res)


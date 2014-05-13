# -*- coding: utf-8 -*-
import random

def pass_generator():
    """Generates a pronunceable password"""
    vowls = ['a','e','i','o','u']
    mixers = ['w','r','t','p','s','d','f','g','j','l','c','b','n','m']

    alpha_lenght = random.randint(4,7)

    psw = ''
    for i in xrange(alpha_lenght):
        psw +=  random.choice(mixers) + random.choice(vowls)

    numeric_length = random.randint(2,3)

    for i in xrange(numeric_length):
        psw += str(random.randint(0,9))

    return psw
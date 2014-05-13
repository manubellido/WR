# -*- coding: utf-8 -*-

class BaseConverter(object):

    decimal_digits = "0123456789"
    
    def __init__(self, digits):
        self.digits = digits
    
    def from_decimal(self, i):
        i = [c for c in str(i)]
        return self.convert(i, self.decimal_digits, self.digits)
    
    def to_decimal(self, s):
        return int(''.join(self.convert(s, self.digits, self.decimal_digits)))
   
    @staticmethod 
    def convert(number_as_digits, fromdigits, todigits):
        # make an integer out of the number
        x = 0
        for digit in number_as_digits:
           x = x * len(fromdigits) + fromdigits.index(digit)
    
        # create the result in base 'len(todigits)'
        if x == 0:
            res = todigits[0]
        else:
            res = []
            while x > 0:
                digit = x % len(todigits)
                #res = todigits[digit] + res
                res.insert(0, todigits[digit])
                x = int(x / len(todigits))
        return res

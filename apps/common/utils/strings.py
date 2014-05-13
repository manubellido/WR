# -*- coding: utf-8 -*- 

import re
from common.utils.iterables import grouper

def str_in_chunks(source, chunk_size, padding=''):
    parts = []
    for e in grouper(chunk_size, source, padding):
        parts.append(''.join(e))
    return parts

def multiple_whitespace_to_single_space(value):
    pattern = re.compile(r'\s+')
    return re.sub(pattern, ' ', value)

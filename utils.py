#!/usr/bin/env python
# -*- coding: utf-8 -*-
URL_CHARS = ('abcdefghijklmnopqrstuvwxyz'
             'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
             '1234567890$-_.+!*\'(),')


def to_url_name(name):
    result = ''
    for c in name:
        if c not in URL_CHARS:
            result += '-'
        else:
            result += c
    return result.strip().lower()



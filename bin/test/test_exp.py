#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : lhr (airhenry@gmail.com)
# @Link    : http://about.me/air.henry


from ln_front import Exp,interpreter
import yaml
import  pytest
yaml.warnings({'YAMLLoadWarning': False})

import os
def test_eval_simple():
    # interpreter([1,2,3])
    # os.chdir('')
    d={'def X': 'world'}
    d=[{'def A': 'world'}, {'good': 'A'},'A']
    d=[
       {'defun good': [['B'],'B','B']},
       {'def A': 'sss'},
       {'good': ['CCC']},
       'A',
        {'sh ls': []},
        {'sh_map txt ls': []}
    ]
    # d=[{'def X': 'world'}]
    # d=['B']
    print(interpreter(d))

def test_eval_def():
    d=[{'def A': 'world'}, {'good': 'A'}]
    e=interpreter(d)
    print(e)


def test_eval_def():
    d='''
- def A: worldddd
- good: A    
    
    '''
    d=yaml.load(d)
    e=interpreter(d)
    print(e)

def test_eval_defun():
    d='''
- defun func1: worldddd
- func1: A    
    
    '''
    d=yaml.load(d)
    e=interpreter(d)
    print(e)

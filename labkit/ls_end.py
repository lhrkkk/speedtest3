#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : lhr (airhenry@gmail.com)
# @Link    : http://about.me/air.henry


import argparse
import json
# import click
import typer


def push_pbs(bq, module_name, single_element, parameters={}):
    # TODO:修改所有用到push_compute的地方, 接口变了.  目前用在generate这样的sample上了,
    # 还有一个推送的过程再ensemble.map函数里面
    '''
    push a task to the compute queue

    :param module_name: the module to call
    :param parameters: the parameters
    :return: True if succeed
    '''
    message = {}
    # message['module_name'] = module_name
    # message['single_element'] = single_element
    message['cmd'] = module_name
    message['arg'] = single_element

    # message['parameters'] = parameters
    bq.use('pbs')
    bq.put(json.dumps(message), ttr=86400000)
    return True


DEBUG = False

# @click.command()
# @click.argument('beanstalk_server')
# @click.argument('port')
# @wrap_for_cython


def pushend():
    '''
    parse a conf(dict) and run it

    :param tree:
    :return:
    '''

    parser = argparse.ArgumentParser(description="""
    Put end singal to the labkit queue.
    """)
    port = 11300
    parser.add_argument("beanstalk_server",
                        help="hostname of beanstalk server")
    args = parser.parse_args()
    beanstalk_server = args.beanstalk_server
    # import beanstalkc
    # bq = beanstalkc.Connection(host=beanstalk_server, port=port)
    import greenstalk
    with greenstalk.Client((beanstalk_server, 11300)) as bq:
        push_pbs(bq, 'end', 'end')


def main():
    pushend()
    # typer.run(pushend)


if __name__ == '__main__':
    main()

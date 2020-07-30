#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : lhr (airhenry@gmail.com)
# @Link    : http://about.me/air.henry


'''
worker requirements:
环境变量:
export PYTHONPATH=/vagrant/labkit:$PYTHONPATH
export PATH=/vagrant/g09:$PATH

'''


import argparse
import os
import json
import traceback
# import click


# def bean_worker(bq):
#     '''
#     a single job deal circle

#     :return:
#     '''


# @click.command()
# @click.argument('beanstalk_server')
# def manage_worker(beanstalk_server):


def manage_worker():
    import os
    import sys
    from multiprocessing.dummy import Pool as ThreadPool

    parser = argparse.ArgumentParser(description="""
    labkit worker.
    """)
    parser.add_argument("beanstalk_server",
                        help="hostname of beanstalk server")
    args = parser.parse_args()
    beanstalk_server = args.beanstalk_server

    hostname = os.popen("hostname").read().strip()
    if hostname != 'core.local':
        thread_number = int(
            os.popen("cat /proc/cpuinfo |grep processor|wc -l").read())
    else:
        thread_number = 4

    # print thread_number
    pool = ThreadPool(thread_number)
    file_list = [x for x in range(thread_number)]
    results = pool.map(lambda placeholder: worker(
        beanstalk_server, placeholder), file_list)

    pool.close()
    pool.join()

    os.system("ssh "+beanstalk_server+" killall beanstalkd")


def worker(beanstalk_server, placeholder, beanstalk_port=11300):
    '''
    start worker loop
    :param queue_names:
    :return:
    '''
    # import beanstalkc
    # bq = beanstalkc.Connection(host=beanstalk_server, port=beanstalk_port)
    import greenstalk
    with greenstalk.Client((beanstalk_server, 11300)) as bq:
        queue_names = ["pbs"]

        for i in queue_names:
            bq.watch(i)
        # print bq.watching()

        # print ("current-job-ready", bq.stats_tube('pbs')['current-jobs-ready'])

        # while bq.stats_tube('pbs')['current-jobs-ready'] > 0:
        while 1:
            # print "current-job-ready", bq.stats_tube('pbs')['current-jobs-ready']
            job = bq.reserve(timeout=1)
            if not job:
                continue
            try:

                # deal with the message
                message = json.loads(job.body)
                # print message
                # log.debug("message is: %s" % message)
                origin_path = os.path.abspath(os.curdir)
                module_name = message['cmd']
                single_element = message['arg']
                if module_name == 'end':
                    job.release()
                    break

                os.system(module_name+' ' + single_element)
                job.delete()
                continue
                # if result:
                #     print("==========", result)
                #     job.delete()
                #     # # TODO: 执行失败不能直接 bury
                #     # else:
                #     #     job.bury()

            except:
                traceback.print_exc()
                if job:
                    job.bury()
            # finally:
                # continue


def main():
    manage_worker()


if __name__ == '__main__':
    main()

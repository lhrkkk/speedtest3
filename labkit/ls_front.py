#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : lhr (airhenry@gmail.com)
# @Link    : http://about.me/air.henry


# import click
import os
import json
import argparse
import yaml
# yaml.warnings({'YAMLLoadWarning': False})


def push_pbs(bq, module_name, single_element, parameters={}):
    # TODO:修改所有用到push_compute的地方, 接口变了.  目前用在generate这样的sample上了, 还有一个推送的过程再ensemble.map函数里面
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


# @click.command()
# @click.argument('filelistname')
# @click.argument('single_cmd')
# @click.argument('beanstalk_server')
# def sub(filelistname, single_cmd, beanstalk_server, beanstalk_port=11300):
#     '''Submit tasks or current workplace to PBS
#     '''

#     # os.system('lll')
#     # print   "good"
#     # return

#     print(filelistname, single_cmd, beanstalk_server)
#     # return
#     import beanstalkc
#     bq = beanstalkc.Connection(host=beanstalk_server, port=beanstalk_port)
#     for file in open(filelistname, 'r').readlines():
#         # print file
#         push_pbs(bq, single_cmd, file)
#     return True


DEBUG = False


def eval_tree(tree, tree_path, context, beanstalk_server, port):
    '''
    parse a conf(dict) and run it

    :param tree:
    :return:
    '''
    # import beanstalkc
    import json
    import time

    # bq = beanstalkc.Connection(host=beanstalk_server, port=port)
    import greenstalk
    with greenstalk.Client((beanstalk_server, 11300)) as bq:
        if type(tree) == list:
            ans = []
            last_dir = os.path.abspath('start')
            for index, item in enumerate(tree):
                # ans.append(eval_tree(item, tree_path + [index], context))
                # cur_dir=cur_dir.replace(' ','_').replace('\/','_').replace("'",'_')

                if item.has_key('sh'):
                    # cur_dir = str(index+1) +'.'+ str(item['sh']['cmd']).replace(' ','_')
                    cur_dir = str(index+1) + '.' + \
                        str(item['sh']['cmd']).split(' ')[0].replace(' ', '_')
                    cur_dir = os.path.abspath(cur_dir)
                    cmdstr = 'cp -rf '+last_dir+' '+'"'+cur_dir+'"'
                    if not os.path.exists(cur_dir):
                        os.system(cmdstr)
                    message = {}
                    message['dir'] = cur_dir
                    message['cmd'] = item['sh']['cmd']

                    cmdstr = 'cd ' + '"'+message['dir'] + '"'
                    cmdstr = cmdstr + '&&' + message['cmd']
                    if DEBUG:
                        print(cmdstr)
                    else:
                        os.system(cmdstr)

                elif item.has_key('sh_map'):
                    cur_dir = str(index+1) + '.' + \
                        str(item['sh_map']['cmd']).replace(' ', '_')
                    cur_dir = os.path.abspath(cur_dir)
                    cmdstr = 'cp -rf '+last_dir+' '+'"'+cur_dir+'"'
                    if not os.path.exists(cur_dir):
                        os.system(cmdstr)

                    findcmd = "find " + cur_dir + " |grep \.txt$"
                    filelist = os.popen(findcmd).readlines()
                    print(filelist)
                    # time.sleep(1000)cc
                    for i in filelist:
                        # message={}
                        # message['dir']=cur_dir
                        # message['cmd']=item['sh_map']['cmd']
                        # message['arg']=i
                        # if DEBUG:
                        #     print(message)
                        #     continue
                        # else:
                        #     bq.use('compute')
                        #     bq.put(json.dumps(message), ttr=TTR)
                        if DEBUG:
                            print(item, i)
                            continue
                        else:
                            push_pbs(bq, item['sh_map']['cmd'], i)
                time.sleep(1)
                if not DEBUG:

                    while bq.stats_tube('pbs')['current-jobs-ready'] != 0 or bq.stats_tube('pbs')[
                            'current-jobs-reserved'] != 0:
                        time.sleep(1)

                last_dir = cur_dir
            # moved to ls_end
            # push_pbs(bq,'end','end')
            return ans
        else:
            # push_pbs(bq,'end','end')
            return False


def load_yaml_file(filename):
    '''
    根据文件名加载yml配置文件, 先调用jinja模板渲染, 然后再解析. 最后返回解析后的字典.
    :param filename: 配置文件名
    :return: 解析后的字典
    '''
    f = open(filename, 'r')
    # rendered= jinja2.Template(f.read()).render(jinja='jinjia2')
    rendered = f.read()
    tree = yaml.load(rendered)
    return tree


# @click.command()
# @click.argument('yml_file_name')
# @click.argument('beanstalk_server')
# def run_yaml_file(yml_file_name, beanstalk_server='localhost', beanstalk_port=11300):
def run_yaml_file():
    '''
    run a yml file. parse the file to dict and run it

    '''
    # filename=single_element['filename']

    parser = argparse.ArgumentParser(description="""
    Start the labkit front.
    """)
    beanstalk_port = 11300
    parser.add_argument("yml_file_name",
                        help="recipe file name")
    parser.add_argument("beanstalk_server",
                        help="hostname of beanstalk server")
    args = parser.parse_args()
    beanstalk_server = args.beanstalk_server
    filename = args.yml_file_name
    task_folder = os.path.abspath(os.path.dirname(filename))
    task_name = os.path.basename(task_folder).split('.')[0]

    working_folder = os.path.join(task_folder, task_name + '.running')
    in_folder = os.path.join(task_folder, task_name + '.in')
    ans_folder = os.path.join(task_folder, task_name + '.ans')
    algorithm = load_yaml_file(filename)

    # 开始和结束都重置context TODO: 应该要重置的, 断点续运行的问题.
    # set_context({})

    # print(algorithm)
    context = {
        'working_folder': working_folder,
        'in_folder': in_folder,
        'ans_folder': ans_folder
    }

    print(algorithm)

    ans = eval_tree(algorithm, [], context,
                    beanstalk_server, port=beanstalk_port)

    # ans=eval_tree_local(algorithm)
    # print(ans)
    # set_context({})

    return ans


def main():
    run_yaml_file()


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
import sys, traceback
import os
import shutil
import requests
import time
import grequests
import itertools
from itertools import product
import multiprocessing as mp
from multiprocessing import Pool
import logging
import subprocess
from subprocess import check_call
import codecs
from xml.etree import ElementTree as ET

from git import Repo

print 'core num: ' + str(mp.cpu_count())
print 'python version:' + sys.version
print 'create sailfish index Started......'

argvs = sys.argv
argc = len(argvs)

if (argc != 3):
    print 'Usage: # python %s out-dir filename(index_list)' % argvs[0]
    quit()

logger = mp.log_to_stderr(logging.DEBUG)

out_dname = argvs[1]
print out_dname

def read_input():
    f = open(argvs[2])
    ret_list = []

    for i in f.readlines():
        i = i.strip()
        if len(i) < 1:
            continue
        ret_list = ret_list + [i]

    f.close
    return ret_list

def makeDir(dname):
    if os.path.exists(dname) is False:
        os.mkdir(dname)
        print '%s (dir) created.' % dname
    else:
        print '%s (dir) is already exists.' % dname

def print_tree(directory):
    for root, dirs, files in os.walk(directory):
        #yield root
        for file in files:
            yield os.path.join(root, file)

def create_dl_list(index_list):
    ret = []
    for item in index_list:
        list = item.split(',')
        item_dir = out_dname + '/' + list[0]
        makeDir(item_dir)
        dl_path = item_dir + '/' + list[1].split('/')[-1]
        print 'downloading-file: ' + dl_path
        if os.path.isfile(dl_path) or os.path.isfile(dl_path.replace('.gz', '')):
            print '>>>>>>>>>> This file is already exists. continue next.'
            continue
        ret.append(list[1])
    return ret

def grequests_async(dl_list, idx_list):
    rs = (grequests.get(url) for url in dl_list)
    for r in grequests.map(rs):
        print r.url + ' >>>>>>>>>><Response>' + str(r.status_code)
        #print idx_list[0]
        #print str(r.url).split('/')[-1]

        out_listitem = next(itertools.ifilter(lambda x:x.find(str(r.url)) > -1, idx_list), None)
        #print out_listitem

        file_name = str(r.url).split('/')[-1]
        out_dir = out_dname + '/' + out_listitem.split(',')[0]
        if os.path.isfile(out_dir + '/' + file_name):
            print '%s is already exists.' % out_dir + '/' + file_name
        else:
            print 'creat-file in ' + out_dir
            os.chdir(out_dir)
            f = open(file_name, 'w')
            f.write(r.content)
            f.close

def run_cmd(cmd):
    print ' '.join(cmd)
    str_cmd = ' '.join(cmd)
    cmd_relist = str_cmd.split(' ')
    print cmd_relist
    subprocess.check_call(cmd_relist)

def generate_cmds(script, keys, vals):

    """
    Generate list of commands from script name, option names, and sets of value
    >>> cmds = gene_cmds_normal('python run.py', ['A', 'B'], [['1', '2'], ['x', 'y']])
    >>> list(cmds)  #doctest: +NORMALIZE_WHITESPACE
    [['python', 'run.py', '--A 1', '--B 2'], ['python', 'run.py', '--A x', '--B y']]

    """
    script = script.split()
    for val in vals:
        #print val
        yield script + ['%s %s' % (k, v) for (k, v) in zip(keys, val)]

def make_param(path):
    dir = path.rsplit('/',1)[0]

    if not os.path.isfile(dir + '/' + 'kmerEquivClasses.bin'):
        return [path.replace('.gz', ''), dir, '20']
    else:
        return []

def unpack_and_make_filelist(idx_list):
    index_files = []
    for file in print_tree(out_dname):
        #print file
        root, ext = os.path.splitext(file)
        if ext == '.gz':
            subprocess.check_call(["gunzip","-fd",file])
            index_files.append(file)
        elif ext == '.fa':
            #print root.split('/')[-2]
            listchk = next(itertools.ifilter(lambda x:x.find(root.split('/')[-2]) > -1, idx_list), None)
            if listchk is not None:
                index_files.append(file)
    print index_files
    index_files = sorted(set(index_files), key=index_files.index)
    return index_files

def main():
    try:
        input_index_list = []
        input_index_list = read_input()
        print 'length of index_list: ' + str(len(input_index_list))
        
        makeDir(out_dname)
        os.chdir(out_dname)
        print 'moved to %s' % os.getcwd()

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> download sailfish index-files ...'
        dl_url_list = []
        dl_url_list = create_dl_list(input_index_list)

        if len(dl_url_list) > 0:
            print 'start download-jobs...'
            grequests_async(dl_url_list, input_index_list)
            print 'all download-jobs finished.'
        else:
            print 'no execute download-jobs.'

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> unpacking and make-list sailfish index-files...'
        index_files = []
        index_files = unpack_and_make_filelist(input_index_list)
        print index_files

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> executing sailfish index...'
        param_list = [make_param(str(x)) for x in index_files]
        print param_list
        while param_list.count([]) > 0:
            param_list.remove([])
        if len(param_list) > 0:
            cmds = generate_cmds('sailfish index --force', ['-t', '-o', '--kmerSize'], param_list)
            [ run_cmd(x) for x in cmds ]
            #if mp.cpu_count() > 1:
            #    pool = Pool(mp.cpu_count())
            #    callback = pool.map_async(run_cmd, cmds).get()
            #else:
            #    print 'cpu is single core.'
            #    [ run_cmd(x) for x in cmds ]
        else:
            print 'sailfish indexes already created.'

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> script ended :)'

    except KeyboardInterrupt:
        print ">>>>>>>>>>>>>>>>> Caught KeyboardInterrupt. Terminating workers..."
        pool.terminate()
        sys.exit(1)
    except:
        info = sys.exc_info()
        tbinfo = traceback.format_tb( info[2] )
        print 'Error Info...'.ljust( 80, '=' )
        for tbi in tbinfo:
            print tbi
        print '  %s' % str( info[1] )
        print '\n'.rjust( 85, '=' )
        sys.exit(1)

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
import sys, traceback
import os
import shutil
import requests
import time
import grequests
import itertools
from itertools import product
from itertools import chain
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
print 'make_sailfish_index.py Started......'

argvs = sys.argv
argc = len(argvs)

if (argc != 3):
    print 'Usage: # python %s mount_dirname ref_dirname' % argvs[0]
    quit()

logger = mp.log_to_stderr(logging.DEBUG)

mountdir = argvs[1]
if not mountdir.endswith('/'):
    mountdir = mountdir + '/'

ref_dir = argvs[2]
if not ref_dir.endswith('/'):
    ref_dir = ref_dir + '/'

blah = "no callback"
out_dname = mountdir + 'sailfish_index/'
out_dname_bowtie = mountdir + 'bowtie2_index/'

def read_input():
    f = open(argvs[1])
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

def run_cmd(cmd):
    str_cmd = ' '.join(cmd).replace("-dummy ", "")
    print str_cmd
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
        yield script + ['%s %s' % (k, v) for (k, v) in zip(keys, val)]

def make_param(ref):
    idx_dir = out_dname + ref.split('/')[-1].replace(".fa","")

    if not os.path.isdir(idx_dir):
        makeDir(idx_dir)
        return [ref, idx_dir, '20']
    else:
        return []

def make_param_b(ref):
    idx_dir = out_dname_bowtie + ref.split('/')[-1].replace(".fa","")

    if not os.path.isdir(idx_dir):
        makeDir(idx_dir)
        return [ref, idx_dir]
    else:
        return []

def create_indexlist(ref_dir):
    index_files = []
    for file in print_tree(ref_dir):
        #print file
        root, ext = os.path.splitext(file)
        if ext == '.fa':
            #print root.split('/')[-2]
            #listchk = next(itertools.ifilter(lambda x:x.find(root.split('/')[-2]) > -1, idx_list), None)
            #if listchk is not None:
            index_files.append(file)
    index_files = sorted(set(index_files), key=index_files.index)
    return index_files

def mycallback(x):
    global blah
    blah = "called back"
    print("My callback " + str(x))

def main():
    try:
        os.environ["PATH"] = os.environ["PATH"] + ':' + os.environ["HOME"] + "/src/Sailfish-0.6.3-Linux_x86-64/bin:" + os.environ["HOME"] + "/src/bowtie2-2.2.5"
        print os.environ["PATH"]
        os.environ["LD_LIBRARY_PATH"] = os.environ["HOME"] + "/src/Sailfish-0.6.3-Linux_x86-64/lib"

        makeDir(out_dname)
        makeDir(out_dname_bowtie)

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> make index list...'
        index_files = []
        index_files = create_indexlist(ref_dir)
        print index_files

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> executing sailfish index...'
        
        param_list_s = [make_param(str(x)) for x in index_files]
        print param_list_s
        while param_list_s.count([]) > 0:
            param_list_s.remove([])
        
        param_list_b = [make_param_b(str(x)) for x in index_files]
        print param_list_b
        while param_list_b.count([]) > 0:
            param_list_b.remove([])
         
        if len(param_list_s) > 0 and len(param_list_b) > 0:
            cmds_s = generate_cmds('sailfish index --force', ['-t', '-o', '--kmerSize'], param_list_s)
            cmds_b = generate_cmds('bowtie2-build', ['-f', ''], param_list_b)
            cmds = chain(cmds_s, cmds_b)
        elif len(param_list_s) > 0:
            cmds = generate_cmds('sailfish index --force', ['-t', '-o', '--kmerSize'], param_list_s)
        elif len(param_list_b) > 0:
            cmds = generate_cmds('bowtie2-build', ['-f', '-dummy'], param_list_b)
        else:
            print 'sailfish and bowtie2 indexes already created.'
            return

        print cmds
        if mp.cpu_count() > 4:
            pool = Pool(4)
            try:
                result = pool.map_async(run_cmd, cmds, callback=mycallback)
                print result.get()
                pool.close()
                print blah
            except KeyboardInterrupt:
                print ">>>>>>>>>>>>>>>>> Caught KeyboardInterrupt. Terminating workers..."
                pool.terminate()
            except Exception, e:
                print '>>>>>>>>>>>>>>>>> got exception: %r, terminating the pool' % (e,)
                pool.terminate()
            finally:
                pool.join()

        else:
            print 'cpu is single core.'
            [ run_cmd(x) for x in cmds ]
 
        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> script ended.'

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

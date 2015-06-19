# -*- coding: utf-8 -*-
import sys, traceback
import os
sys.path.append('/home/myoshimura/src/pyenv/versions/2.7.10/lib/python2.7/site-packages')
import shutil
import requests
import time
import grequests
import itertools
from itertools import product
import subprocess
from subprocess import check_call
import ConfigParser
print "python :" + sys.version

argvs = sys.argv
argc = len(argvs)

print argvs[0] + ' Started.....'

if (argc != 3):
    print 'Usage: # python %s filename(DL_file_list) mount_dir' % argvs[0]
    quit()

mountdir = argvs[2]
if not mountdir.endswith('/'):
    mountdir = mountdir + '/'
out_dname = mountdir + 'transcriptome_ref_fasta'
spike_file = os.getcwd() + '/ERCC.fa'

def exception_handler(request, exception):
    print "Request failed"

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
        for file in files:
            yield os.path.join(root, file)

def create_dl_list(ref_list):
    ret = []
    for item in ref_list:
        item_list = item.split(',')
        dl_path = item_list[1]
        dl_item = item_list[1].split('/')[-1]
        print 'downloading-file: ' + dl_path
        if os.path.isfile(item_list[0] + '.fa'):
            print '>>>>>>>>>> This Ref-file is already exists. continue next.'
            continue
        ret.append(item_list[1])
    return ret

def grequests_async(dl_list, ref_list):
    rs = (grequests.get(url) for url in dl_list)
    for r in grequests.map(rs):
        print r.url + ' >>>>>>>>>><Response>' + str(r.status_code)
        out_listitem = next(itertools.ifilter(lambda x:x.find(str(r.url)) > -1, ref_list), None)
        file_name = out_listitem.split(',')[0] + '.fa'
        if os.path.isfile(out_dname + '/' + file_name):
            print out_dname + '/' + file_name + ' is already exists.'
        else:
            print 'creat-file in ' + out_dname
            f = open(file_name + '.gz', 'w')
            f.write(r.content)
            f.close

def unpack_files():
    ref_files = []
    for file in print_tree(out_dname):
        root, ext = os.path.splitext(file)
        if ext == '.gz':
            subprocess.check_call(["gunzip","-fd",file])
            ref_files.append(file)
        elif ext == '.fa':
            ref_files.append(file)
            ref_files = sorted(set(ref_files), key=ref_files.index)
    return ref_files

def cat_spike():
    for file in print_tree(out_dname):
        root, ext = os.path.splitext(file)
        if ext == '.fa' and not "spike" in file.split('/')[-1]:
            newname = file.replace(".fa", "_spike.fa")
            if not os.path.exists(newname):
                with open(newname, 'w') as f:
                    subprocess.Popen(["cat", file, spike_file], stdout=f)
                    print "created spike-in ref-fasta: " + newname.split('/')[-1]
            else:
                print "spike-in ref-fasta is already exits: " + newname.split('/')[-1]

def main():
    try:
        ref_list = []
        ref_list = read_input()
        print 'length of ref_list: ' + str(len(ref_list))

        makeDir(out_dname)
        os.chdir(out_dname)
        print 'moved to %s' % os.getcwd()

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> download transcritome files ...'

        dl_url_list = []
        dl_url_list = create_dl_list(ref_list)

        if len(dl_url_list) > 0:
            print 'start download-jobs...'
            grequests_async(dl_url_list, ref_list)
            print 'all download-jobs finished.'
        else:
            print 'no execute download-jobs.'

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> unpacking transcritome files...'
        ref_files = []
        ref_files = unpack_files()

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> concatenate spike-seq...'
        cat_spike()

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

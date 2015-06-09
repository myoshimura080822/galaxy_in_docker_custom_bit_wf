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

argvs = sys.argv
argc = len(argvs)

out_dname = '/data/sailfish_index'
bowtie2_idx_dname = ['/data/bowtie2_index/mm9_ucsc/Mus_musculus/UCSC/mm9/Sequence/Bowtie2Index','/data/bowtie2_index/mm10_ucsc/Mus_musculus/UCSC/mm10/Sequence/Bowtie2Index']
loc_dname = '/galaxy-central/tool-data'

if (argc != 3):
    print 'Usage: # python %s filename(Sailfish index_list) filename(Bowtie2 index_list)' % argvs[0]
    quit()

def read_input(name):
    num = 1 if name == 'Sailfish' else 2
    f = open(argvs[num])
    ret_list = []

    for i in f.readlines():
        i = i.strip()
        if len(i) < 1:
            continue
        ret_list = ret_list + [i]

    f.close
    return ret_list

def create_loc_file(index_list):
    f = codecs.open("sailfish_index.loc", "w", "utf-8")
    for item in index_list:
        index_id = item.split(',')[0]
        index_name = item.split(',')[2]
        index_dir = out_dname + '/' + index_id
        str_loc = '%s : %s : %s : %s' % (index_id,index_id,index_name,index_dir)
        print str_loc
        f.write('%s\t%s\t%s\t%s\n' % (index_id,index_id,index_name,index_dir))
    f.close()

def get_bowtie2index_dir(path):
    dir_list = []
    for (root, dirs, files) in os.walk(path):
        for dir in dirs:
            dir_list.append( os.path.join(root,dir).replace("\\", "/") )
    
    dir_chk = filter(lambda x:x.find("Bowtie2Index") > -1, dir_list)
    return dir_chk[0] if len(dir_chk) > 0 else ""

def create_bowtie2_loc_file(index_dir, index_list):
    f = codecs.open("bowtie2_indices.loc", "w", "utf-8")
    for dir_name in index_dir:
        if len(dir_name) > 0:
            item_info = filter(lambda x:x.find(dir_name.split('/')[-6]) > -1, index_list)[0]
            index_id = item_info.split('_')[0]
	    index_name = 'Mouse(' + index_id + ')'
            str_loc = '%s : %s : %s : %s' % (index_id,index_id,index_name,dir_name + '/genome')
            print str_loc
            f.write('%s\t%s\t%s\t%s\n' % (index_id,index_id,index_name,dir_name + '/genome'))
    f.close()

def add_tool_data_table_conf(tree, name, locname):
    root_elm = tree.getroot()
    add_node = ET.Element('table', name=name, comment_char='#')
    snode_col = ET.Element('columns')
    snode_col.text = 'value, dbkey, name, path'
    snode_file = ET.Element('file', path='/galaxy-central/tool-data/' + locname)
    add_node.append(snode_col)
    add_node.append(snode_file)
    root_elm.append(add_node)
    print root_elm.getchildren()[len(root_elm)-1].attrib
    print root_elm.getchildren()[len(root_elm)-1].getchildren()
    tree.write('/galaxy-central/config/tool_data_table_conf.xml')

def main():
    try:
        input_index_list = []
        input_index_list = read_input('Sailfish')
        print 'length of index_list: ' + str(len(input_index_list))
        input_bowtie2_index_list = []
        input_bowtie2_index_list = read_input('Bowtie2')
        print 'length of Bowtie2_index_list: ' + str(len(input_bowtie2_index_list))
        
        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> create sailfish_index.loc...'
        os.chdir(loc_dname)
        create_loc_file(input_index_list)

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> add sailfish index-node to tool_data_table_conf.xml...'
        os.chdir('/galaxy-central/config')
        tree = ET.parse('tool_data_table_conf.xml')
        add_tool_data_table_conf(tree, 'sailfish_custom_indexes', 'sailfish_index.loc')

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> create bowtie2_indices.loc...'
        os.chdir(loc_dname)
        create_bowtie2_loc_file(bowtie2_idx_dname, input_bowtie2_index_list)

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> add bowtie2 index-node to tool_data_table_conf.xml...'
        os.chdir('/galaxy-central/config')
        tree = ET.parse('tool_data_table_conf.xml')

        bowtie2_node = 0
        for e in tree.getiterator():
            if e.get('name') == 'bowtie2_indexes':
                bowtie2_node = 1

        if bowtie2_node == 0:
            add_tool_data_table_conf(tree, 'bowtie2_indexes', 'bowtie2_indices.loc')
        else:
            print 'bowtie2 index-node already created.'

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> script ended :)'

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

# -*- coding: utf-8 -*-
import sys, traceback
import os
import ConfigParser
from git import Repo
from xml.etree import ElementTree as ET
import subprocess
from subprocess import check_call

print 'Install bit-tools Started......'
argvs = sys.argv
argc = len(argvs)

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
workdir = '/galaxy-central'
tooldir = workdir + '/tools'

def add_tool_conf(tree, list):
    root_elm = tree.getroot()
    add_node = ET.Element('section', name='Bit-Tools', id='bittools')
    for name in list:
        snode_tool = ET.Element('tool', file=name)
        add_node.append(snode_tool)
    root_elm.append(add_node)
    print root_elm.getchildren()[len(root_elm)-1].attrib
    print root_elm.getchildren()[len(root_elm)-1].getchildren()
    tree.write('tool_conf.xml.main')

def get_all_xml(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            name, ext = os.path.splitext(file)
            if not '.git' in root and ext == '.xml':
                yield os.path.join(root, file)

def main():
    try:
        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> clone BiT Tools from github...'
        os.chdir(tooldir)
        git_url = 'https://github.com/myoshimura080822/galaxy-mytools_rnaseq.git'
        Repo.clone_from(git_url, 'galaxy-mytools_rnaseq')

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> add BiT tool-node to tool_conf.xml...'
        mytoolsdir = tooldir + '/galaxy-mytools_rnaseq/'
        xml_list = [file.replace(tooldir + '/', "") for file in get_all_xml(mytoolsdir)]
        print (set(xml_list))
        print xml_list

        os.chdir(workdir + '/config')
        tool_tree = ET.parse('tool_conf.xml.main')
        for e in tool_tree.getiterator():
            if e.get('file') in xml_list:
                xml_list.remove(e.get('file'))
                print '%s tool node already created.' % e.get('file')
        print xml_list
        add_tool_conf(tool_tree, xml_list)
        print '>>>>>>>>>>>>>>>>> script ended :)'
        return 0

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
    sys.exit(main())

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

rnatools_repo = 'tools_of_rnaseq_on_docker_galaxy'
pretools_repo = 'tools_of_preanalysis_on_docker_galaxy' 

def add_tool_conf(repo, sectionname, sectionid):
    mytoolsdir = tooldir + '/' + repo + '/'
    xml_list = [file.replace(tooldir + '/', "") for file in get_all_xml(mytoolsdir)]
    print (set(xml_list))
    #print xml_list

    os.chdir(workdir + '/config')
    tool_tree = ET.parse('tool_conf.xml.main')
    for e in tool_tree.getiterator():
        if e.get('file') in xml_list:
            xml_list.remove(e.get('file'))
            print '%s tool node already created.' % e.get('file')
    print xml_list

    root_elm = tool_tree.getroot()
    add_node = ET.Element('section', name=sectionname, id=sectionid)
    for name in xml_list:
        snode_tool = ET.Element('tool', file=name)
        add_node.append(snode_tool)
    root_elm.append(add_node)
    print root_elm.getchildren()[len(root_elm)-1].attrib
    print root_elm.getchildren()[len(root_elm)-1].getchildren()
    tool_tree.write('tool_conf.xml.main')

def get_all_xml(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            name, ext = os.path.splitext(file)
            if not '.git' in root and ext == '.xml':
                yield os.path.join(root, file)

def main():
    try:
        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> clone repository...'
        os.chdir(tooldir)
        git_url_rna = 'https://github.com/myoshimura080822/'+ rnatools_repo +'.git'
        git_url_pre = 'https://github.com/myoshimura080822/'+ pretools_repo +'.git'
        Repo.clone_from(git_url_rna, rnatools_repo)
        Repo.clone_from(git_url_pre, pretools_repo)

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> add tool-node to tool_conf.xml...'
        
        add_tool_conf(rnatools_repo, 'Custom tools of RNAseq', 'custom_tools_of_rnaseq')
        add_tool_conf(pretools_repo, 'Custom tools of Pre-Analysis', 'custom_tools_of_pre')
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

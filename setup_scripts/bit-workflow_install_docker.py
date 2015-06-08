import sys, traceback
import os
from git import Repo
from ConfigParser import SafeConfigParser
import bioblend
from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.workflows import WorkflowClient
import subprocess

dist_dname = '/galaxy-central/config'
wf_dname = dist_dname + '/workflow_file'
repo_name = 'galaxy-workflow_pre_analysis'

GALAXY_URL = 'http://localhost:8080/'
conf = SafeConfigParser()
conf.read(dist_dname + '/galaxy.ini')
API_KEY="admin"

def get_all_ga(directory):
    ret = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            name, ext = os.path.splitext(file)
            if not '.git' in root and ext == '.ga':
                ret.append(os.path.join(root, file))
    return ret

def makeDir(dname):
    if os.path.exists(dname) is False:
        os.mkdir(dname)
        print '%s (dir) created.' % dname
    else:
        print '%s (dir) is already exists.' % dname

def main():
    try:
        gInstance = GalaxyInstance(url = GALAXY_URL, key=API_KEY)
        wClient = WorkflowClient(gInstance)

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> get current workflowlist...'
        gInstance = GalaxyInstance(url = GALAXY_URL, key=API_KEY)
        wClient = WorkflowClient(gInstance)
        dataset = wClient.get_workflows()
        wf_namelist = [x['name'] for x in dataset if x['deleted'] == False]
        print wf_namelist
        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> clone BiT Workflows from github...'
        if not os.path.exists(wf_dname + '/' + repo_name):
            makeDir(wf_dname)
            os.chdir(wf_dname)
            git_url = 'https://github.com/myoshimura080822/' + repo_name + '.git'
            Repo.clone_from(git_url, repo_name)
        else:
            print repo_name + ' already cloned. To update, Please delete, move or rename dir before this script execute.'
            return 0

        print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> delete and inport workflow files...'

        mytoolsdir = wf_dname + '/' + repo_name + '/'
        clone_wf_list = [file.replace(mytoolsdir, "") for file in get_all_ga(mytoolsdir)]
        print clone_wf_list
        delete_itm =[]
        [[ delete_itm.append(y) for y in wf_namelist if y.find(x.replace('.ga','')) > -1] for x in clone_wf_list]
        print delete_itm
        id_list = []
        [[id_list.append(x['id']) for x in dataset if x['name'].find(y) > -1] for y in delete_itm]
        print id_list
        [wClient.delete_workflow(x) for x in id_list]
        print wClient.get_workflows()
        [wClient.import_workflow_from_local_path(file) for file in get_all_ga(mytoolsdir)]
        print wClient.get_workflows()

        print ':::::::::::::::::::::::::::::::::::::::::::'
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

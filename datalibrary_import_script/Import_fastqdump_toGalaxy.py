import sys
import pwd, os

sys.path.append('/home/myoshimura/src/pyenv/versions/2.7.10/lib/python2.7/site-packages')

import subprocess
import time
import datetime
import dateutil.tz
import bioblend
from bioblend import galaxy
from subprocess import CalledProcessError
import collections
import traceback
import multiprocessing as mp
import re
import fnmatch
import commands
import shutil
import lxml.html
import codecs

datetime = datetime.datetime.today().strftime("%Y%m%d%H%M")
#sys.stdout = open(datetime + ".log","w")

print u"Import_fastqdump_toGalaxy.py Started......"

argvs = sys.argv
argc = len(argvs)

if argc < 4:
    print 'Usage: # python %s runfolder-dir docker-mount-dir port-no import_only=F ' % argvs[0]
    quit()

run_dir = argvs[1]
mount_dir = argvs[2]
port_no = argvs[3]

if not run_dir.endswith('/'):
    run_d = run_dir + '/'
else:
    run_d = run_dir
        
if not mount_dir.endswith('/'):
    mount_d = mount_dir + '/'
else:
    mount_d = mount_dir

import_only = False
not_report = False
galaxy_mount_dir = "/data/"

fastqdump = "/home/myoshimura/src/sratoolkit.2.5.2-ubuntu64/bin/fastq-dump"

if argc == 5 :
    if argvs[4] == 'T':
        import_only = True
        galaxy_mount_dir = "/data"

hostname = os.uname()[1]

print "whoami : " + pwd.getpwuid(os.getuid())[0]
print "current_dir : " + os.getcwd()

url = "http://" + hostname + ":" + port_no
admin_email = os.environ.get('GALAXY_DEFAULT_ADMIN_USER', 'admin@galaxy.org')
admin_pass = os.environ.get('GALAXY_DEFAULT_ADMIN_PASSWORD', 'admin')
gi = galaxy.GalaxyInstance(url=url, email=admin_email, password=admin_pass)

home_dir = commands.getoutput("echo $HOME")

def create_datalib(dname, dist=""):
    print "Create Data library......"

    dlib = [x for x in gi.libraries.get_libraries() if x['name'].strip() == dname.strip()]
    if len(dlib) > 0:
        print gi.libraries.get_libraries()
        raise Exception, dname + ' is already exist.'


    new_lib = gi.libraries.create_library(dname, dist)
    new_lib_id = new_lib['id']
    return new_lib_id

def get_import_files(dir_name, exp):
    for root, dirs, files in os.walk(dir_name):
        if (exp == ".sra") :
            file_list = [ os.path.join(root, filename) for filename in files if exp == os.path.splitext(filename)[1]]
        else:
            file_list = '\n'.join( [ os.path.join(root, filename) for filename in files ] )
            print file_list
            file_list = '\n'.join( [ os.path.join(root, filename) for filename in files if exp in os.path.splitext(filename)] )

    return file_list

def import_data(new_lib_id, name_list):
    gi.libraries.upload_from_galaxy_filesystem(
        new_lib_id,
        name_list,
        file_type = 'fastq.gz',
        link_data_only = 'link_to_files'
    )
    time.sleep(1)

    # Wait for uploads to complete
    #while True:
    #    try:
    #        ret = subprocess.check_output(["qstat"])
    #        ret_list = ret.split('\n')
    #        if not len([x for x in ret_list if 'upload' in x]):
    #            break
    #        time.sleep(3)
    #    except CalledProcessError as inst:
    #        if inst.returncode == 153: #queue is empty
    #            break
    #        else:
    #            raise

    #time.sleep(10)
    print "Finished importing test data."

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

def run_fastqdump(f, out):
    cmd = [fastqdump, f, '-O', out, '--gzip']
    print ' '.join(cmd)
    str_cmd = ' '.join(cmd)
    cmd_relist = str_cmd.split(' ')
    print cmd_relist
    ret = subprocess.check_output(cmd_relist)
    return ret

def generate_cmd(script, keys, vals):

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

def main():
    try:
    	if os.path.exists(run_d) is False:
            raise Exception, run_d + ' is not found.'
    	if os.path.exists(mount_d) is False:
            raise Exception, mount_d + ' is not found.'
        
        if not import_only: 
            file_list = get_import_files(run_d, ".sra")
            #print file_list
            out_d = mount_d + run_d.split('/')[-2] + '_' + datetime + "/"
            print "output-dir : " + out_d
            makeDir(out_d)
            [run_fastqdump(x, out_d) for x in file_list]
        else:
            out_d = run_d
        
        imp_file_list = get_import_files(out_d, ".gz")
        if len(imp_file_list) == 0:
            raise Exception, 'import files not found.'
                        
        imp_file_list = imp_file_list.replace(os.path.abspath(mount_d), galaxy_mount_dir)
        print imp_file_list
    	
        ### import DataLibrary 
        lib_name = run_d.split('/')[-2]
        data_dirname = lib_name + "_" + datetime
        new_lib_id = create_datalib(data_dirname)
        import_data(new_lib_id, imp_file_list)

    	print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> end of script'
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

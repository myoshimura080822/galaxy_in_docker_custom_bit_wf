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

print u"Import_bal2fastq_toGalaxy.py Started......"

argvs = sys.argv
argc = len(argvs)

if argc < 4 or argc == 5:
    print 'Usage: # python %s runfolder-dir docker-mount-dir port-no import_only=F not_report=F ' % argvs[0]
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
#mount_d = mount_d + "next_seq_fastqgz/"

import_only = False
not_report = False
galaxy_mount_dir = "/data"

if argc > 4 :
    if argvs[4] == 'T':
        import_only = True
        galaxy_mount_dir = "/data"
        mount_d = mount_d.replace("next_seq_fastqgz/", "")
    if argvs[5] == 'T':
        not_report = True

hostname = os.uname()[1]

print "whoami : " + pwd.getpwuid(os.getuid())[0]
print "current_dir : " + os.getcwd()

url = "http://" + hostname + ":" + port_no
admin_email = os.environ.get('GALAXY_DEFAULT_ADMIN_USER', 'admin@galaxy.org')
admin_pass = os.environ.get('GALAXY_DEFAULT_ADMIN_PASSWORD', 'admin')
gi = galaxy.GalaxyInstance(url=url, email=admin_email, password=admin_pass)

home_dir = commands.getoutput("echo $HOME")
report_dir = home_dir + "/bcl2fastq_report"
print "report_dir: " + report_dir

def create_datalib(dname, dist=""):
    print "Create Data library......"

    dlib = [x for x in gi.libraries.get_libraries() if x['name'].strip() == dname.strip()]
    if len(dlib) > 0:
        print gi.libraries.get_libraries()
        raise Exception, dname + ' is already exist.'


    new_lib = gi.libraries.create_library(dname, dist)
    new_lib_id = new_lib['id']
    return new_lib_id

def get_import_files(dir_name):
    for root, dirs, files in os.walk(dir_name):
        if "Reports" in dirs and "Stats" in dirs:
            file_list = '\n'.join( [ os.path.join(root, filename) for filename in files if ".gz" == os.path.splitext(filename)[1]] )

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

def run_bcl2fastq(cmd):
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
            out_d = mount_d + run_d.split('/')[-2] + '_' + datetime + "/"
            print "output-dir : " + out_d
            makeDir(out_d)

            param_list = ['--runfolder-dir', '--interop-dir', '--input-dir', '--sample-sheet', 
                            '--output-dir', '--stats-dir', '--reports-dir']
            value_list = [[run_d, run_d + 'InterOp', run_d + 'Data/Intensities/BaseCalls', run_d + 'SampleSheet.csv',
                            out_d, out_d + 'Stats', out_d + 'Reports']]
            cmd = generate_cmd(home_dir + '/src/bcl2fastq --no-lane-splitting', param_list, value_list)
        
            ### exec bcl2fastq
            [ run_bcl2fastq(x) for x in cmd ]
        else:
            out_d = run_d
        
        ### rename fastq.gz
        pair = False
        
        if "aruyo" in ["aruyo" if "R2" in file_n else "naiyo" for file_n in print_tree(out_d)]:
            print "paired-end"
            pair = True
        else:
            print "single-end"

        for out_file in print_tree(out_d):
            if pair:
                p = re.compile("(.*?)(\_S\d+)(\_R\d+)(\_\d+\.fastq.gz)")
                m = p.match(out_file)
                if m != None:
                    newname = m.group(1) + m.group(3).replace('R','') + ".fastq.gz"
                    print newname
                    os.rename(out_file, newname)
            else:
                p = re.compile("(.*?)(\_S\d+)(\_R\d+)(\_\d+\.fastq.gz)")
                m = p.match(out_file)
                if m != None:
                    newname = m.group(1) + ".fastq.gz"
                    print newname
                    os.rename(out_file, newname)
    	
        imp_file_list = get_import_files(out_d)
        if len(imp_file_list) == 0:
            raise Exception, 'import files not found.'
                        
        imp_file_list = imp_file_list.replace(os.path.abspath(mount_d), galaxy_mount_dir)
        print imp_file_list
    	
        ### import DataLibrary 
        lib_name = run_d.split('/')[-2]
        data_dirname = lib_name + "_" + datetime
        new_lib_id = create_datalib(data_dirname)
        import_data(new_lib_id, imp_file_list)

        if not not_report:
            ### copy to Report-Dir
            cp_repo_dir = report_dir + '/' + data_dirname
            print cp_repo_dir
            shutil.copytree(out_d + '/Reports/html', cp_repo_dir)
        
            fp = codecs.open(report_dir + '/index.html', encoding="utf-8")
            content = fp.read()
            fp.close()

            dom = lxml.html.fromstring(content)
            parent = dom.get_element_by_id('report_link')
            print parent
            new_item = lxml.html.Element('a', {'href':"#", 'class':"btn btn-success btn-lg btn-block",
                'onClick':"popup_modeless('" + data_dirname + "/index.html')"})
            new_item.text = data_dirname
            parent.append(new_item)
            rewrite = lxml.html.tostring(dom, encoding="utf-8")
            print rewrite
            w_fp = open(report_dir + '/index.html', "w") 
            w_fp.write(rewrite)
            w_fp.close()

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

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

datetime = datetime.datetime.today().strftime("%Y%m%d%H%M")
#sys.stdout = open(datetime + ".log","w")

print u"ImportDataLibrariesScript.py Started......"

argvs = sys.argv
argc = len(argvs)

if (argc != 6):
    print 'Usage: # python %s file-dir(can parent-dir) docker-mount-dir port-no filetype fileext' % argvs[0]
    quit()

import_dir = argvs[1]
mount_dir = argvs[2]
port_no = argvs[3]
file_type = argvs[4]
file_ext = argvs[5]

hostname = os.uname()[1]

print "whoami : " + pwd.getpwuid(os.getuid())[0]
print "pwd : " + os.getcwd()

url = "http://" + hostname + ":" + port_no
admin_email = os.environ.get('GALAXY_DEFAULT_ADMIN_USER', 'admin@galaxy.org')
admin_pass = os.environ.get('GALAXY_DEFAULT_ADMIN_PASSWORD', 'admin')
gi = galaxy.GalaxyInstance(url=url, email=admin_email, password=admin_pass)

path_list = []

def create_datalib(dname, dist=""):
    print "Create Data library......"

    dlib = [x for x in gi.libraries.get_libraries() if x['name'].strip() == dname.strip()]
    if len(dlib) > 0:
        print gi.libraries.get_libraries()
        raise Exception, dname + ' is already exist.'


    new_lib = gi.libraries.create_library(dname, dist)
    new_lib_id = new_lib['id']
    return new_lib_id

def merge_data(path):
    makeDir(path)

class MultiDict(collections.MutableMapping):
    def __init__(self):
        self._dict = {}

    def __setitem__(self, key, value):
        t = self._dict.get(key, ())
        self._dict[key] = t + (value,)

    def __getitem__(self, key):
        return self._dict[key]

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __contains__(self, item):
        return item in self._dict

    def __str__(self):
        return str(self._dict)

def create_pair_path(root_dir):
    path_list = MultiDict()
    for root, dirs, files in os.walk(root_dir):
        #first = os.path.basename(os.path.normpath(root))
        dirname = os.path.dirname(root)
        #print dirname
        #print files
        if len(files) > 0:
            #file_list = [os.path.join(root, filename) for filename in files if 'fastq.gz' in filename and 'L001' in filename]
            #file_list2 = [os.path.join(root, filename) for filename in files if 'fastq.gz' in filename and 'L002' in filename]
            file_list = [os.path.join(root, filename) for filename in files if 'fastq' in filename and '001.fastq' in filename]
            file_list2 = [os.path.join(root, filename) for filename in files if 'fastq' in filename and '002.fastq' in filename]
            if len(file_list) > 0:
                path_list[os.path.basename(dirname)+"_001"] = file_list
            if len(file_list2) > 0:
                path_list[os.path.basename(dirname)+"_002"] = file_list2
    
    if len(path_list) == 0:
        print "can't create pair list in input-dir."
        return ""

    #print path_list
    keys_list = path_list.keys()
    print keys_list
    lane_01 = list(path_list[keys_list[1]][0])
    lane_01.sort()
    print len(lane_01)
    lane_02 = list(path_list[keys_list[0]][0])
    lane_02.sort()
    print len(lane_02)

    #pair_filepath = [[f1, [f2 for f2 in lane_02 if str(os.path.basename(f1)).replace("L001","L002") in f2][0]] for f1 in lane_01]
    pair_filepath = [[f1, [f2 for f2 in lane_02 if str(os.path.basename(f1)).replace("_001","_002") in f2][0]] for f1 in lane_01]
    print pair_filepath
    print len(pair_filepath)

    return pair_filepath

def merge_pair_fastq(list, outdir):

    ret_list = []
    for i, item in enumerate(list):
        output_filename = outdir + str(os.path.basename(item[0])).replace("_001","").replace("_R","_")
        print output_filename

        if not os.path.isfile(output_filename):
            with open(output_filename, 'w') as f:
                #proc = subprocess.Popen(["zcat", item[0], item[1]], env=os.environ, stdout=f, stderr=subprocess.PIPE)
                proc = subprocess.Popen(["cat", item[0], item[1]], env=os.environ, stdout=f, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            retcode = proc.returncode
            del proc

            if retcode == 1:
                raise ScriptRunningError('zcat command could not run of \$ %s\n%s' % (str(output_filename), str(stderr)))
            else:
                ret_list.append(output_filename)
        else:
            print output_filename + "is already created."

    return '\n'.join(ret_list)

def get_import_files(dir_name):
    for root, dirs, files in os.walk(dir_name):
        file_list = '\n'.join( [ os.path.join(root, filename) for filename in files if '.' + file_ext == os.path.splitext(filename)[1]] )
    return file_list

class ScriptRunningError(Exception):
    pass

def import_data(new_lib_id, name_list):
    gi.libraries.upload_from_galaxy_filesystem(
        new_lib_id,
        name_list,
        file_type = file_type,
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

def main():
    try:
    	if os.path.exists(import_dir) is False:
            raise Exception, import_dir + ' is not found.'
    	if os.path.exists(mount_dir) is False:
            raise Exception, mount_dir + ' is not found.'
    
	if not import_dir.endswith('/'):
            import_d = import_dir + '/'
    	    print import_d
	else:
	    import_d = import_dir

	if not mount_dir.endswith('/'):
            mount_d = mount_dir + '/'
    	    print mount_d
    	
	pair_filepath = create_pair_path(import_d)
    
        if not pair_filepath == "":
    	    output_dir = import_d + "merged_fastq_" + datetime + "/"
    	    makeDir(output_dir)
    	    ret_file_list = merge_pair_fastq(pair_filepath, output_dir)
        else:
    	    ret_file_list = get_import_files(import_d)
    	
        
	if len(ret_file_list) == 0:
	    raise Exception, 'import files is not found.'
	
	ret_file_list = ret_file_list.replace(os.path.abspath(mount_dir), '/data')
        print ret_file_list
    	
	# Create DataLibrary 
        lib_name = import_dir.split('/')[-1]
        new_lib_id = create_datalib(lib_name + "_" + datetime)
        import_data(new_lib_id, ret_file_list)

    	print ':::::::::::::::::::::::::::::::::::::::::::'
        print '>>>>>>>>>>>>>>>>> end of script'

        #sys.stdout.close()
        #sys.stdout = sys.__stdout__
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

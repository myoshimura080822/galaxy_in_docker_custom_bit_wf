# Base image
FROM myoshimura080822/galaxy_in_docker_base:160408

# Put my hand up as maintainer
MAINTAINER Mika Yoshimura <myoshimura080822@gmail.com>

# Include all needed scripts from the host
ADD galaxy_lib /galaxy/galaxy_lib
ADD setup_scripts /galaxy/setup_scripts
ADD modefied_tools /galaxy/modefied_tools

# Replace modefied setting files
RUN cp /galaxy/galaxy_lib/galaxy.ini.docker_sample /galaxy-central/config/galaxy.ini && \
    cp /galaxy/galaxy_lib/job_conf.xml.docker_sample /galaxy-central/config/job_conf.xml && \
    cp /galaxy/galaxy_lib/datatypes_conf.xml.docker_sample /galaxy-central/config/datatypes_conf.xml && \
# Replace modefied lib files
    mv /galaxy-central/lib/galaxy/datatypes/data.py /galaxy-central/lib/galaxy/datatypes/data.py_bk && \
    mv /galaxy-central/lib/galaxy/datatypes/sniff.py /galaxy-central/lib/galaxy/datatypes/sniff.py_bk && \
    mv /galaxy-central/tools/data_source/upload.py /galaxy-central/tools/data_source/upload.py_bk && \
    cp /galaxy/galaxy_lib/data.py /galaxy-central/lib/galaxy/datatypes/ && \
    cp /galaxy/galaxy_lib/sniff.py /galaxy-central/lib/galaxy/datatypes/ && \
    cp /galaxy/galaxy_lib/upload.py /galaxy-central/tools/data_source/ && \
# Make import_data dir
    mkdir /galaxy-central/config/import_data && \
    cd /galaxy-central/config/import_data;ln -s /data/transcriptome_ref_fasta;ln -s /data/adapter_primer;ln -s /data/Homo_sapiens_genome;ln -s /data/Mus_musculus_genome && \
# Install Custom Bit-Tools
    python /galaxy/setup_scripts/bit-tools_install_docker.py && \
    cp -a /galaxy-central/config/tool_conf.xml.main /galaxy-central/config/tool_conf.xml && \
# replace migrate ToolSheds tools
    mv /galaxy/modefied_tools/for_latest_fastq-mcf.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/jjohnson/fastq_mcf/b61f1466ce8f/fastq_mcf/fastq-mcf.xml && \
    mv /galaxy/modefied_tools/for_latest_rgFastQC.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/devteam/fastqc/28d39af2dd06/fastqc/rgFastQC.xml && \
    cp /galaxy/modefied_tools/edger_robust/edgeR.* /shed_tools/toolshed.g2.bx.psu.edu/repos/fcaramia/edger/6324eefd9e91/edger/ && \
# Setting Index
    cp /galaxy/setup_scripts/setting_tools_index.py /galaxy/ && \
    cp /galaxy/setup_scripts/index_file_mrna.txt /galaxy/ && \
    cp /galaxy/setup_scripts/index_file_list_tophat.txt /galaxy/ && \
    cp /galaxy/setup_scripts/index_file_list_hisat2.txt /galaxy/ && \
    cp -a /galaxy-central/config/tool_data_table_conf.xml.sample /galaxy-central/config/tool_data_table_conf.xml && \
    python /galaxy/setting_tools_index.py /galaxy/index_file_mrna.txt /galaxy/index_file_list_tophat.txt /galaxy/index_file_list_hisat2.txt && \
# Import Bit-workflow to admin-user 
    cp /galaxy/setup_scripts/bit-workflow_install_docker.py /galaxy/bit-workflow_install_docker.py && \
    cp /galaxy/setup_scripts/bit-workflow_install_docker.sh /galaxy-central/bit-workflow_install_docker.sh && \
# for postgresql upgrade
    cp /galaxy/galaxy_lib/auth_conf.xml.sample /galaxy/ && \
    chmod 755 /galaxy/auth_conf.xml.sample && \
    chown galaxy. /galaxy/auth_conf.xml.sample

RUN sh /galaxy-central/bit-workflow_install_docker.sh

# modified postgresql.conf
ENV PGPORT=15432 \
    GALAXY_CONFIG_DATABASE_CONNECTION=postgresql://galaxy:galaxy@localhost:15432/galaxy

# Define default command
CMD ["/usr/bin/startup"]

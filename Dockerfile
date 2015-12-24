# Base image
FROM myoshimura080822/galaxy_in_docker_base:151018

# Put my hand up as maintainer
MAINTAINER Mika Yoshimura <myoshimura080822@gmail.com>

#Install OS tools we'll need
#RUN \
#    apt-get -y update && \

#Install additional R Pkg
#WORKDIR /galaxy
#ADD setup_scripts/install_additional.R /galaxy/install_additional.R
#RUN R -e 'source("/galaxy/install_additional.R")'

# Replace modefied setting files
WORKDIR /galaxy-central
COPY ./galaxy.ini.docker_sample /galaxy-central/config/galaxy.ini
COPY ./job_conf.xml.docker_sample /galaxy-central/config/job_conf.xml
COPY ./datatypes_conf.xml.docker_sample /galaxy-central/config/datatypes_conf.xml

# Replace modefied lib files
RUN mv /galaxy-central/lib/galaxy/datatypes/data.py /galaxy-central/lib/galaxy/datatypes/data.py_bk && \
    mv /galaxy-central/lib/galaxy/datatypes/sniff.py /galaxy-central/lib/galaxy/datatypes/sniff.py_bk && \
    mv /galaxy-central/tools/data_source/upload.py /galaxy-central/tools/data_source/upload.py_bk
COPY galaxy_lib/data.py /galaxy-central/lib/galaxy/datatypes/data.py
COPY galaxy_lib/sniff.py /galaxy-central/lib/galaxy/datatypes/sniff.py
COPY galaxy_lib/upload.py /galaxy-central/tools/data_source/upload.py

# Make import_data dir
RUN mkdir /galaxy-central/config/import_data && \
    cd /galaxy-central/config/import_data;ln -s /data/transcriptome_ref_fasta;ln -s /data/adapter_primer

# Install Custom Bit-Tools
WORKDIR /galaxy
COPY setup_scripts/bit-tools_install_docker.py /galaxy/bit-tools_install_docker.py
RUN python /galaxy/bit-tools_install_docker.py && \
    cp -a /galaxy-central/config/tool_conf.xml.main /galaxy-central/config/tool_conf.xml

# replace migrate ToolSheds tools
COPY modefied_tools/for_latest_fastq-mcf.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/jjohnson/fastq_mcf/b61f1466ce8f/fastq_mcf/fastq-mcf.xml
COPY modefied_tools/for_latest_rgFastQC.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/devteam/fastqc/8c650f7f76e9/fastqc/rgFastQC.xml
COPY modefied_tools/edger_robust/edgeR.pl /shed_tools/toolshed.g2.bx.psu.edu/repos/fcaramia/edger/6324eefd9e91/edger/edgeR.pl
COPY modefied_tools/edger_robust/edgeR.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/fcaramia/edger/6324eefd9e91/edger/edgeR.xml

# Setting Sailfish and Bowtie2 or Tophat Index
COPY setup_scripts/setting_tools_index.py /galaxy/setting_tools_index.py
COPY setup_scripts/index_file_list.txt /galaxy/index_file_list.txt
COPY setup_scripts/index_file_list_tophat.txt /galaxy/index_file_list_tophat.txt
RUN cp -a /galaxy-central/config/tool_data_table_conf.xml.sample /galaxy-central/config/tool_data_table_conf.xml && \
    python /galaxy/setting_tools_index.py index_file_list.txt F && \
    python /galaxy/setting_tools_index.py index_file_list_tophat.txt T

# Install ToolShed-tools
WORKDIR /galaxy-central
RUN install-repository "--url https://toolshed.g2.bx.psu.edu/ -o devteam --name cufflinks -r a1ea9af8d5f4 --panel-section-name NGS-tools"

# Import Bit-workflow to admin-user
COPY setup_scripts/bit-workflow_install_docker.py /galaxy/bit-workflow_install_docker.py
COPY setup_scripts/bit-workflow_install_docker.sh /galaxy-central/bit-workflow_install_docker.sh
RUN sh /galaxy-central/bit-workflow_install_docker.sh

# for postgresql upgrade
COPY galaxy_lib/auth_conf.xml.sample /galaxy/auth_conf.xml.sample
RUN chmod 755 /galaxy/auth_conf.xml.sample
RUN chown galaxy:galaxy /galaxy/auth_conf.xml.sample

# Mark folders as imported from the host.
VOLUME ["/export/", "/data/", "/var/lib/docker"]

# modified postgresql.conf
ENV PGPORT 15432
ENV GALAXY_CONFIG_DATABASE_CONNECTION postgresql://galaxy:galaxy@localhost:15432/galaxy

# Expose port 80 (webserver), 21 (FTP server), 8800 (Proxy)
EXPOSE :80
EXPOSE :21
EXPOSE :8800

# Define working directory
WORKDIR /galaxy-central

# Define default command
CMD ["/usr/bin/startup"]

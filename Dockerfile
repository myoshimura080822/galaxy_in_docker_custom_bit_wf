# Base image
FROM myoshimura080822/galaxy_in_docker_custom

# Put my hand up as maintainer
MAINTAINER Mika Yoshimura <myoshimura080822@gmail.com>

#Install OS tools we'll need
RUN \
    apt-get -y update && \
    apt-get -y install imagemagick && \
    apt-get -y install pandoc && \
    apt-get -y install libcurl4-gnutls-dev && \
    apt-get -y install libglu1-mesa-dev freeglut3-dev mesa-common-dev

#Install additional R Pkg
WORKDIR /galaxy
ADD setup_scripts/install_additional.R /galaxy/install_additional.R
RUN R -e 'source("/galaxy/install_additional.R")'

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
    cd /galaxy-central/config/import_data;ln -s /data/ref_fasta;ln -s /data/adapter_primer

# Install Sailfish
WORKDIR /galaxy
RUN wget https://github.com/kingsfordgroup/sailfish/releases/download/v0.6.3/Sailfish-0.6.3-Linux_x86-64.tar.gz && \
    tar -zxvf Sailfish-0.6.3-Linux_x86-64.tar.gz && \
    rm Sailfish-0.6.3-Linux_x86-64.tar.gz && \
    mv /galaxy/Sailfish-0.6.3-Linux_x86-64/lib/libz.so.1 /galaxy/Sailfish-0.6.3-Linux_x86-64/lib/libz.so.1_bk
ENV PATH $PATH:/galaxy/Sailfish-0.6.3-Linux_x86-64/bin
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/galaxy/Sailfish-0.6.3-Linux_x86-64/lib

# Clone Bug-fixed ToolFactory
RUN git clone https://github.com/myoshimura080822/galaxy-mytools_ToolFactory.git && \
    mv /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/rgToolFactory.py /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/rgToolFactory_BK.py && \
    cp /galaxy/galaxy-mytools_ToolFactory/rgToolFactory.py /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/ && \
    mv /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/rgToolFactory.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/rgToolFactory_BK.xml && \
    cp /galaxy/galaxy-mytools_ToolFactory/rgToolFactory.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/

# Install Custom Bit-Tools
COPY setup_scripts/bit-tools_install_docker.py /galaxy/bit-tools_install_docker.py
RUN python /galaxy/bit-tools_install_docker.py && \
    cp -a /galaxy-central/config/tool_conf.xml.main /galaxy-central/config/tool_conf.xml

# Install custom for docker-tools
#COPY setup_scripts/for-hiseq-tools_install_docker.py /galaxy/for-hiseq-tools_install_docker.py
#RUN python /galaxy/for-hiseq-tools_install_docker.py && \
#    cp -a /galaxy-central/config/tool_conf.xml.main /galaxy-central/config/tool_conf.xml

# replace migrate ToolSheds tools
COPY modefied_tools/for_latest_fastq-mcf.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/jjohnson/fastq_mcf/b61f1466ce8f/fastq_mcf/fastq-mcf.xml
COPY modefied_tools/for_latest_rgFastQC.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/devteam/fastqc/8c650f7f76e9/fastqc/rgFastQC.xml

# Setting Index
COPY setup_scripts/setting_tools_index.py /galaxy/setting_tools_index.py
COPY setup_scripts/index_file_list.txt /galaxy/index_file_list.txt
COPY setup_scripts/index_file_list_bowtie2.txt /galaxy/index_file_list_bowtie2.txt
RUN cp -a /galaxy-central/config/tool_data_table_conf.xml.sample /galaxy-central/config/tool_data_table_conf.xml && \
    python /galaxy/setting_tools_index.py index_file_list.txt index_file_list_bowtie2.txt

# Import Bit-workflow to admin-user
WORKDIR /galaxy-central
COPY setup_scripts/bit-workflow_install_docker.py /galaxy/bit-workflow_install_docker.py
COPY setup_scripts/bit-workflow_install_docker.sh /galaxy-central/bit-workflow_install_docker.sh
RUN sh /galaxy-central/bit-workflow_install_docker.sh

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

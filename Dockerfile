# Base image
FROM myoshimura080822/galaxy_in_docker_custom

# Put my hand up as maintainer
MAINTAINER Mika Yoshimura <myoshimura080822@gmail.com>

# Replace modified galaxy.ini
ADD ./galaxy.ini.docker_sample /galaxy-central/config/galaxy.ini

# Make import_data dir
RUN mkdir /galaxy-central/config/import_data

# Install Sailfish
WORKDIR /galaxy
RUN wget https://github.com/kingsfordgroup/sailfish/releases/download/v0.6.3/Sailfish-0.6.3-Linux_x86-64.tar.gz && \
    tar -zxvf Sailfish-0.6.3-Linux_x86-64.tar.gz && \
    rm Sailfish-0.6.3-Linux_x86-64.tar.gz && \
    mv /galaxy/Sailfish-0.6.3-Linux_x86-64/lib/libz.so.1 /galaxy/Sailfish-0.6.3-Linux_x86-64/lib/libz.so.1_bk
ENV PATH $PATH:/galaxy/Sailfish-0.6.3-Linux_x86-64/bin
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/galaxy/Sailfish-0.6.3-Linux_x86-64/lib

# Clone Bug-fixed ToolFactory
WORKDIR /galaxy
RUN git clone https://github.com/myoshimura080822/galaxy-mytools_ToolFactory.git && \
    mv /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/rgToolFactory.py /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/rgToolFactory_BK.py && \
    cp /galaxy/galaxy-mytools_ToolFactory/rgToolFactory.py /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/ && \
    mv /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/rgToolFactory.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/rgToolFactory_BK.xml && \
    cp /galaxy/galaxy-mytools_ToolFactory/rgToolFactory.xml /shed_tools/toolshed.g2.bx.psu.edu/repos/fubar/toolfactory/e9ebb410930d/toolfactory/

# Install Custom Bit-Tools
WORKDIR /galaxy
ADD ./bit-tools_install_docker.py /galaxy/bit-tools_install_docker.py
RUN python /galaxy/bit-tools_install_docker.py && \
    cp -a /galaxy-central/config/tool_conf.xml.main /galaxy-central/config/tool_conf.xml

# replace migrate Bit-Tools file (for latest galaxy)
ADD ./for_latest_GetDatasetDatPath.xml /galaxy-central/tools/galaxy-mytools_rnaseq/GetDatasetDatPath/GetDatasetDatPath.xml
ADD ./for_latest_SailfishConvertAndMergeColumnForDEG.xml /galaxy-central/tools/galaxy-mytools_rnaseq/Sailfish_ConvertAndMergeColumnForDEG/SailfishConvertAndMergeColumnForDEG.xml
ADD ./for_latest_eXpressConvertAndMergeDataForDEG.xml /galaxy-central/tools/galaxy-mytools_rnaseq/eXpressConvertAndMergeDataForDEG.xml

# Setting Sailfish-index
WORKDIR /galaxy
ADD ./setting_sailfish_index.py /galaxy/setting_sailfish_index.py
ADD ./index_file_list.txt /galaxy/index_file_list.txt
RUN cp -a /galaxy-central/config/tool_data_table_conf.xml.sample /galaxy-central/config/tool_data_table_conf.xml && \
    python /galaxy/setting_sailfish_index.py index_file_list.txt

# Import Bit-woorkflow to admin-user
WORKDIR /galaxy-central
ADD ./bit-workflow_install_docker.py /galaxy/bit-workflow_install_docker.py
ADD ./bit-workflow_install_docker.sh /galaxy-central/bit-workflow_install_docker.sh
RUN sh /galaxy-central/bit-workflow_install_docker.sh

# Mark folders as imported from the host.
VOLUME ["/export/", "/data/", "/var/lib/docker"]

# Expose port 80 (webserver), 21 (FTP server), 8800 (Proxy)
EXPOSE :80
EXPOSE :21
EXPOSE :8800

# Define working directory
WORKDIR /galaxy-central

# Define default command
CMD ["/usr/bin/startup"]

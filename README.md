# galaxy_in_docker_custom_bit_wf

This extension add NGS analysis tools for Dockerfiles in the bgruening/docker-galaxy-stable images from Björn A. Grüning.

https://github.com/bgruening/docker-galaxy-stable

base image

https://github.com/myoshimura080822/galaxy_in_docker_custom

# History(Tag)
- myoshimura080822/galaxy_in_docker_bitwf:160607
  - modified wrong path of sailfish-0.9.2 wrapper tool 
- myoshimura080822/galaxy_in_docker_bitwf:160520
  - add new workflow for wig convert to bigwig format
    - genome_RNA-seq_BAM_to_BigWig.ga 
- myoshimura080822/galaxy_in_docker_bitwf:0512
  - modefied galaxy.conf docker setting
    - from "usr/bin/docker -d" to "usr/bin/docker -d -s vfs" 
- myoshimura080822/galaxy_in_docker_bitwf:160411
  - add Human UCSC hg38 for genome-reference
  - add genome-mapped RNA-seq Workflow
    - genome_RNA-seq_01_Paired-end(mapping_in_HISAT2).ga
    - genome_RNA-seq_01_Paired-end(mapping_in_Tophat2).ga
    - genome_RNA-seq_01_Single-end(mapping_in_HISAT2).ga
    - genome_RNA-seq_01_Single-end(mapping_in_Tophat2).ga
- myoshimura080822/galaxy_in_docker_bitwf:160408
  - add index path(.lov file) for tophat and hisat2

# Galaxy Image for RNA-Seq WF

RNA-Seq用WFおよびツールが配置されたGalaxy環境のコンテナです。 

## Base Image
[bgruening/galaxy-stable](https://github.com/bgruening/docker-galaxy-stable)

* based on Ubuntu 14.04 LTS
* all recommended Galaxy requirements are installed

## Index
* [Installed packages](#installed-pkg)
* [Installed tools](#installed-tools)
* [Installed workflow](#installed-wf)
* [Usage](#usage)
* [Users & Passwords](#user--passowrds)
* [Restarting Galaxy](#restarting-galaxy)
* [Licence (MIT)](#license-mit)

## <a id="installed-pkg">Installed packages
* tree
* zsh, oh_my_zsh
* vim
* R 3.2.2
* Python 2.7.6

## <a id="installed-tools">Installed galaxy tools
* Fastqmcf
* FastQC
* Bowtie2
* samtools_flagstat
* [Sailfish](http://www.cs.cmu.edu/~ckingsf/software/sailfish/)
* eXpress
* edgeR, [edgeR robust](http://imlspenticton.uzh.ch/robinson_lab/edgeR_robust/)
* [SCDE](http://hms-dbmi.github.io/scde/)
* [destiny](https://www.helmholtz-muenchen.de/icb/destiny)
* Toolfactory, Toolfactory2

## <a id="installed-wf">Installed workflow

**RNA-seq_01_Paired-end(Quantifying in Sailfish)**

![sailfish-pairWF](https://github.com/myoshimura080822/galaxy_in_docker_custom_bit_wf/blob/master/images/RNA-seq_01_Paired-end(Quantifying%20in%20Sailfish).png)

**RNA-seq_01_Paired-end(Quantifying in eXpress)**

![express-pairWF](https://github.com/myoshimura080822/galaxy_in_docker_custom_bit_wf/blob/master/images/RNA-seq_01_Paired-end(Quantifying%20in%20eXpress).png)

**RNA-seq_01_Single-end(Quantifying in eXpress)**

![express-singleWF](https://github.com/myoshimura080822/galaxy_in_docker_custom_bit_wf/blob/master/images/RNA-seq_01_Single-end(Quantifying%20in%20eXpress).png)

**RNA-seq_01_Single-end(Quantifying in Sailfish)**

![sailfish-singleWF](https://github.com/myoshimura080822/galaxy_in_docker_custom_bit_wf/blob/master/images/RNA-seq_01_Single-end(Quantifying%20in%20Sailfish).png)

**RNA-seq_02_Plotting of QC-all,corr,H-clustering and PCA)**

![QC_PCA_Corr](https://github.com/myoshimura080822/galaxy_in_docker_custom_bit_wf/blob/master/images/RNA-seq_02_PlottingQC_PCA_Corr.png)

**RNA-seq_03(Analysis of DEG in SCDE)**

![DEG_on_SCDE](https://github.com/myoshimura080822/galaxy_in_docker_custom_bit_wf/blob/master/images/RNA-seq_03(Analysis%20of%20DEG%20in%20SCDE).png)

**RNA-seq_03(Analysis of DEG in edgeR)**

![DEG_on_edgeR](https://github.com/myoshimura080822/galaxy_in_docker_custom_bit_wf/blob/master/images/RNA-seq_03(Analysis%20of%20DEG%20in%20edgeR).png)

**RNA-seq_03(Analysis of multi-DEG in edgeR_robust, ANOVA-like)**

![DEG_on_edgeR](https://github.com/myoshimura080822/galaxy_in_docker_custom_bit_wf/blob/master/images/RNA-seq_03(Analysis%20of%20DEG%20in%20edgeR).png)

## <a id="usage">Usage
* [docker](https://docs.docker.com/installation/)のインストールが必要です
* dockerコマンドの詳細な解説は[docker manual](http://docs.docker.io/)を参照してください

### 1.マウントディレクトリの作成
* dockerイメージは読み取り専用であり、コンテナ内部の変更は再起動時にリセットされます。
* docker run の前に、以下の2つをホストの任意の場所に作成する必要があります。
 * 1) コンテナで永続的に扱うデータをエクスポートするディレクトリ (``/export/``にマウント)
 * 2) Galaxyで使用するファイルをインポートするディレクトリ (``/data/``にマウント)
* ``/data/``にマウントするディレクトリ配下に、以下の名前のディレクトリを作成してください<<必須>>
 * adapter_primer
 * transcriptome_ref_fasta

### 2.Sailfish, Bowtie2のIndex作成
* 1) ホスト環境にSailfish, Bowtie2をDL
 * [Sailfish DL](http://www.cs.cmu.edu/~ckingsf/software/sailfish/downloads.html)
 * [Bowtie2 DL](http://sourceforge.net/projects/bowtie-bio/files/bowtie2/2.2.5/)
* 2) git clone
```bash
git clone https://github.com/myoshimura080822/galaxy_in_docker_custom_bit_wf.git
cd galaxy_in_docker_custom_bit_wf
```
* 3) Ref-fasta DL
 * すでにDLしている場合は 4) を実行してください 
```bash
cd ./setup_reference_and_index/
python setup_TranscriptomeRef_in_Galaxy.py index_file_list.txt <</data/ mount Dir path>>
```
 * ``/data/ mount Dir`` 配下にtranscriptome_ref_fastaディレクトリが作成されます
 * DL fasta
  * human/Ensembl(GRCh38 cdna_all,release-82)
  * human/UCSC(hg38 refMrna,17-Jun-2015)
  * mouse/Ensembl(GRCm38 cdna_all,release-82)
  * mouse/UCSC(mm10 refMrna,15-Jun-2015)
  * ERCC (for Spike)

* 4) Create Sailfish / Bowtie2 Index
```bash
python create_sailfish_and_Bowtie2_index.py <</data/ mount Dir path>> <<Ref-fasta DL-Dir path>> <<Sailfish fullpath>> <<Bowtie2 fullpath>>
```
* ``/data/ mount Dir`` 配下にsailfish_index, bowtie2_indexディレクトリが作成されます
* Galaxyツールの設定ファイルに記述されているパスになるため、renameはしないでください

### 3.docker run
```bash
docker run -d -p 8080:80 -v /home/user/galaxy_storage/:/export/ -v /home/user/galaxy_data:/data/ myoshimura080822/galaxy_in_docker_custom_bit_wf
```
* ``docker run`` コンテナを起動
* ``-p 8080:80`` コンテナのポート80(Apacheサーバー)がホストの8080で有効になる(変更可)
* ``http://<<hostname or IP Address>>:8080`` Galaxyにアクセスするurl
* ``myoshimura080822/galaxy_in_docker_custom_bit_wf`` イメージ/コンテナ名
* ``-d`` コンテナをデーモンモードで起動
* ``-v /home/user/galaxy_storage/:/export/`` コンテナの ``/export/``に``/home/user/galaxy_storage``をマウントする
  * 上記のディレクトリに対し、``startup.sh`` スクリプト(starting Apache, PostgreSQL and Galaxy) が以下の操作を行う
    * ``/export/`` が空の場合、[PostgreSQL](http://www.postgresql.org/) DB, Galaxy DB, Shed Tools, Tool Dependencies やその他config scriptsを``/export/``に移動し、シンボリックリンクが作成される
    * ``/export/`` が空でない場合、中身は変更せずシンボリックリンクだけが作成される
* ``-v /home/user/galaxy_data:/data/`` コンテナの ``/data/``に``/home/user/galaxy_data``をマウントする

## <a id='user--passowrds'>Users & Passwords
* galaxy admin username ``admin@galaxy.org`` 
* password ``admin``

## <a id='restarting-galaxy'>Restarting Galaxy
* 以下のコマンドをホスト環境で実行します
 *  ```docker exec <container name> supervisorctl restart galaxy:```

**コンテナ内での再起動は使用できません (export配下のファイルが消去されます)**

## <a id="license-mit">Licence (MIT)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

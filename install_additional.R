is.installed <- function(mypkg){
    is.element(mypkg, installed.packages()[,1])
}

if (!is.installed("ggplot2")){
    install.packages('ggplot2', repos="http://cran.rstudio.com/")
}

if (!is.installed("pairsD3")){
    install.packages('pairsD3', repos="http://cran.rstudio.com/")
}

if (!is.installed("magrittr")){
    install.packages('magrittr', repos="http://cran.rstudio.com/")
}

if (!is.installed("matrixStats")){
    install.packages('matrixStats', repos="http://cran.rstudio.com/")
}

if (!is.installed("pvclust")){
    install.packages('pvclust', repos="http://cran.rstudio.com/")
}

if (!is.installed("devtools")){
    install.packages('devtools', repos="http://cran.rstudio.com/")
}

if (!is.installed("factoextra")){
    devtools::install_github("kassambara/factoextra")
}

if (!is.installed("rgl")){
    install.packages('rgl', repos="http://cran.rstudio.com/")
}

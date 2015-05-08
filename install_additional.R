is.installed <- function(mypkg){
    is.element(mypkg, installed.packages()[,1])
}

if (!is.installed("ggplot2")){
    install.packages('ggplot2', repos="http://cran.rstudio.com/")
}

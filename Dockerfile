FROM guiguem/root-docker:latest

MAINTAINER Mathieu Guigue "Mathieu.Guigue@pnnl.gov"

RUN /bin/bash -c "pip install pip --upgrade &&\
    source /setup.sh &&\
    pip -V &&\
    git clone -b master https://github.com/project8/morpho &&\
    pip install /morpho/. &&\
    cd /morpho/examples && morpho -c morpho_test/scripts/morpho_linear_fit.yaml"

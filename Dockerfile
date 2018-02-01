FROM guiguem/root-docker:python3

MAINTAINER Mathieu Guigue "Mathieu.Guigue@pnnl.gov"

ADD . /morpho

RUN /bin/bash -c "apt-get remove -y python-pip &&\
    source /setup.sh &&\
    wget https://bootstrap.pypa.io/get-pip.py &&\
    python3 get-pip.py pip setuptools wheel &&\
    pip3 install /morpho/."

CMD ['source /setup.sh']

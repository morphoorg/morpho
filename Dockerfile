FROM guiguem/root-docker:latest

MAINTAINER Mathieu Guigue "Mathieu.Guigue@pnnl.gov"

ADD . /morpho

RUN /bin/bash -c "apt-get remove -y python-pip &&\
    source /setup.sh &&\
    wget https://bootstrap.pypa.io/get-pip.py &&\
    python  get-pip.py setuptools pip wheel &&\
    pip install /morpho/."

CMD ['source /setup.sh']

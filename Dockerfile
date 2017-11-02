FROM rootproject/root-ubuntu16:6.10

MAINTAINER Mathieu Guigue "Mathieu.Guigue@pnnl.gov"

RUN export PYTHONPATH=/usr/local/root/lib/root
USER root
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y libhdf5-serial-dev python-pip
RUN git clone -b master https://github.com/project8/morpho
RUN pip install pip --upgrade && pip install /morpho/.

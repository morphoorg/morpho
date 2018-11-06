FROM guiguem/root-docker:python3

MAINTAINER Mathieu Guigue "Mathieu.Guigue@pnnl.gov"

COPY . /morpho

RUN /bin/bash -c "source /setup.sh &&\
    python3 --version &&\
    which pip &&\
    pip3 install pkgconfig pip --upgrade &&\
    pip3 install /morpho/."

CMD ['source /setup.sh']

# FROM rootproject/root-ubuntu16:6.12

# MAINTAINER Mathieu Guigue "Mathieu.Guigue@pnnl.gov"

# COPY . /morpho

# USER root

# RUN /bin/bash -c "apt-get update && apt-get install wget"

# RUN /bin/bash -c "wget https://bootstrap.pypa.io/get-pip.py &&\
# python3 get-pip.py pip setuptools wheel pkgconfig &&\
# cd /morpho &&\
# pip install ."

# # RUN /bin/bash -c "source /setup.sh &&\
# #     python3 --version &&\
# #     which pip &&\
# #     pip3 install pkgconfig pip --upgrade &&\
# #     pip3 install /morpho/."

# # CMD ['source /setup.sh']
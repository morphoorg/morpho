FROM lukasheinrich/cern-root:latest

ADD . /morpho
RUN which python
RUN /usr/local/bin/pip install /morpho

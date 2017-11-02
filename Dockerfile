FROM rootproject/root-ubuntu16

MAINTAINER Mathieu Guigue "Mathieu.Guigue@pnnl.gov"


# Run the following commands as super user (root):
USER root

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y libhdf5-serial-dev python-pip

# Create a user that does not have root privileges 
ARG username=physicist
RUN userdel builder && useradd --create-home --home-dir /home/${username} ${username}
ENV HOME /home/${username}



RUN git clone -b master https://github.com/project8/morpho
RUN chown -R ${username} /morpho

# Switch to our newly created user
USER ${username}
RUN whoami
# RUN pip install --upgrade pip==9.0.1 
# RUN pip install numpy==1.13.1 six==1.11.0

RUN pip install /morpho/.
RUN export PYTHONPATH=/usr/local/root/lib/root
RUN cd /morpho/examples && morpho -c morpho_test/scripts/morpho_linear_fit.yaml 

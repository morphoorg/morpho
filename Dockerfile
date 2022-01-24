FROM ghcr.io/morphoorg/morpho-docker:main as morpho_common


ENV MORPHO_TAG=v2.7.2
ENV MORPHO_REPO_PREFIX=$REPO_DIR/morpho/$MORPHO_TAG
ENV MORPHO_INSTALL_PREFIX=$INSTALL_DIR/morpho/$MORPHO_TAG

# fix for pystan (otherwise it cannot find gcc)
ENV CC=gcc
ENV CXX=g++

RUN mkdir -p $MORPHO_REPO_PREFIX &&\
    mkdir -p $MORPHO_INSTALL_PREFIX

########################
FROM morpho_common as morpho_done

COPY --chown=linuxbrew bin $MORPHO_REPO_PREFIX/bin
COPY --chown=linuxbrew examples $MORPHO_REPO_PREFIX/examples
COPY --chown=linuxbrew morpho $MORPHO_REPO_PREFIX/morpho
COPY --chown=linuxbrew setup.py $MORPHO_REPO_PREFIX/setup.py
COPY --chown=linuxbrew .git $MORPHO_REPO_PREFIX/.git
COPY --chown=linuxbrew tests $MORPHO_REPO_PREFIX/tests

WORKDIR $MORPHO_REPO_PREFIX

RUN . /home/linuxbrew/.bash_profile &&\
    pip3 install .




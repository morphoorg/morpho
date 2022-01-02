FROM ghcr.io/morphoorg/morpho-docker:main as morpho_common

ENV MORPHO_TAG=v2.7.2
ENV MORPHO_REPO_PREFIX=$REPO_DIR/morpho/$MORPHO_TAG
ENV MORPHO_INSTALL_PREFIX=$INSTALL_DIR/morpho/$MORPHO_TAG

RUN mkdir -p $MORPHO_REPO_PREFIX &&\
    mkdir -p $MORPHO_INSTALL_PREFIX

########################
FROM morpho_common as morpho_done

COPY bin $MORPHO_REPO_PREFIX/bin
COPY examples $MORPHO_REPO_PREFIX/examples
COPY morpho $MORPHO_REPO_PREFIX/morpho
COPY setup.py $MORPHO_REPO_PREFIX/setup.py
COPY .git $MORPHO_REPO_PREFIX/.git
COPY tests $MORPHO_REPO_PREFIX/tests

RUN cd $MORPHO_REPO_PREFIX &&\
    pip3 install . --prefix $MORPHO_INSTALL_PREFIX &&\
    /bin/true


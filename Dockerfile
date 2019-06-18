FROM kbase/sdkbase2:python
MAINTAINER Kelly Huang <kellyhuang@berkeley.edu>
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update

CMD ["brew install imagemagick"]
CMD ["brew install wget"]


RUN apt-get update -qq && \
    apt-get install -yq --no-install-recommends \
                                                git \
                                                less \
                                                libdatetime-perl \
                                                libxml-simple-perl \
                                                libdigest-md5-perl \
                                                bioperl

RUN apt-get install -y cpanminus
RUN apt-get -y install gcc

RUN cpanm -v Error
RUN cpanm -v LWP::UserAgent
# RUN cpanm -v LWP::Protocol::https
RUN cpanm -v Tie::IxHash

RUN apt-get -y install ncbi-blast+

RUN apt-get -y install emboss
# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]

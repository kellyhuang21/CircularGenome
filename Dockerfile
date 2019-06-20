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

RUN cd /opt && \
    apt-get update -qq && \
    apt-get install -yq --no-install-recommends \
                                                git \
                                                less \
                                                wget \
                                                libdatetime-perl \
                                                libxml-simple-perl \
                                                libdigest-md5-perl \
                                                bioperl && \

    apt-get install -y cpanminus && \
    apt-get -y install gcc && \
    cpanm -v Error && \
    cpanm -v LWP::UserAgent && \
    # cpanm -v LWP::Protocol::https && \
    cpanm -v Tie::IxHash && \
    apt-get -y install emboss && \
    curl ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.9.0+-x64-linux.tar.gz > ncbi-blast-2.9.0+-x64-linux.tar.gz && \
    tar xfz ncbi-blast-2.9.0+-x64-linux.tar.gz && \
    rm ncbi-blast-2.9.0+-x64-linux.tar.gz && \
    curl -O -J -L http://www.ualberta.ca/~stothard/downloads/cgview_comparison_tool.zip > cgview_comparison_tool.zip && \
    unzip cgview_comparison_tool.zip && \
    rm cgview_comparison_tool.zip
    # && \
    # export PERL5LIB="${CCT_HOME}"/lib/bioperl-1.2.3:"${CCT_HOME}"/lib/perl_modules:"$PERL5LIB"

ENV CCT_HOME="/opt/cgview_comparison_tool"
ENV PATH="$PATH":"${CCT_HOME}/scripts":/opt/ncbi-blast-2.9.0+/bin
ENV PERL5LIB=${CCT_HOME}/lib/bioperl-1.2.3:${CCT_HOME}/lib/perl_modules:$PERL5LIB
# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
FROM continuumio/miniconda3

RUN apt-get update && apt-get install -y build-essential
RUN pip install pipenv

RUN wget https://s3-us-west-1.amazonaws.com/exp.alpacadb.com/talib/talib_0.4.0-1.deb && \
    dpkg -i talib_0.4.0-1.deb && \
    rm talib_0.4.0-1.deb
RUN echo "usr/local/lib" >> /etc/ld.so.conf && /sbin/ldconfig

ADD Pipfile Pipfile.lock /work/
RUN cd /work && pipenv install

ADD junalgo/ /work/
WORKDIR /work

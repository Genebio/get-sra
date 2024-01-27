FROM python:3.11-bullseye


RUN apt-get update && apt-get install -y pigz

ENV SRA_VERSION=3.0.10
RUN wget https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/${SRA_VERSION}/sratoolkit.${SRA_VERSION}-ubuntu64.tar.gz && \
    tar -xzf sratoolkit.${SRA_VERSION}-ubuntu64.tar.gz && \
    rm sratoolkit.${SRA_VERSION}-ubuntu64.tar.gz

ENV PATH="${PATH}:/sratoolkit.${SRA_VERSION}-ubuntu64/bin/"

WORKDIR /usr/local/src
COPY run.py ./

ENTRYPOINT ["/usr/bin/python3", "/usr/local/src/run.py"]
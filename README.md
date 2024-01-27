# README.md for the get-sra Docker Component

## Overview
The `get-sra` Docker component is a streamlined tool for downloading sequence data from the NCBI's Sequence Read Archive (SRA), including dbGaP-protected data. It wraps the functionality of the SRA Toolkit into a Docker container for ease of use and reproducibility.

## Features
- **SRA Toolkit Integration**: Direct access to SRA Toolkit features in a stable Docker environment.
- **Supports dbGaP Access**: Enables authorized users to download dbGaP-protected data.
- **Efficient Data Retrieval**: Optimized for downloading large datasets with minimal configuration.
- **User-Friendly**: Designed for ease of use with a clear command-line interface.

## Prerequisites
- Docker installed on your machine.
- Access to the internet for downloading data from SRA.
- (Optional) dbGaP authorization keys for accessing protected data.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone git@github.com:Genebio/get-sra.git
   ```
2. **Build the Docker Image**:
   Navigate to the directory containing the Dockerfile and run:
   ```bash
   docker build -t get-sra:1.0.0 .
   ```

## Usage
To use the `get-sra` tool, run the Docker container with the required parameters:

```bash
docker run --rm -it \
    -v [local-directory-path]:/data \
    get-sra:1.0.0 \
    --sra-id [SRA_ID] \
    --output-forward-fastq-gz /data/[forward-filename].fastq.gz \
    --output-reverse-fastq-gz /data/[reverse-filename].fastq.gz \
    --ngc-key-file /data/[keyfile.ngc]
```

### Command-line Arguments
- `--sra-id`: The SRA ID of the file to download (Ex. `SRR23085779`)
- `--ngc-key-file`: (Optional) Path to the dbGaP access key file.
- `--output-forward-fastq-gz`: Path for the output forward strand FASTQ.GZ file.
- `--output-reverse-fastq-gz`: Path for the output reverse strand FASTQ.GZ file.
- `--output-single-fastq-gz`: Path for the output single-end FASTQ.GZ file.

## Troubleshooting and Support
For issues and questions regarding the use of this tool, please refer to the issue tracker in the GitHub repository or contact genebio91@gmail.com.

## Contribution
Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

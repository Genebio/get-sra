import os
import sys
import logging
import argparse
import subprocess
from multiprocessing import cpu_count
from typing import Optional, List


DOWNLOAD_SRA_CONNECTIONS = 8

LOGGER_FORMAT = "%(name)s | line %(lineno)-3d | %(levelname)-8s | %(message)s"
logger = logging.getLogger(name=__file__)


def set_logger(logger_format: str = LOGGER_FORMAT) -> None:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(logger_format))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False


class AddOutputPrefix(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, args: argparse.Namespace,
                 value: str, option_string=None):
        setattr(args, self.dest, os.path.join(outprefix, value))


def parse_args() -> dict:
    parser = argparse.ArgumentParser()

    in_group = parser.add_argument_group("Input")
    in_group.add_argument("--sra-id", type=str, required=True, help="SRA id")
    in_group.add_argument("--ngc-key-file", help="dbGaP access key file")

    out_group = parser.add_argument_group("Output")
    out_group.add_argument("--output-forward-fastq-gz",
                           help="Forward strand fastq.gz file", action=AddOutputPrefix)
    out_group.add_argument("--output-reverse-fastq-gz",
                           help="Reverse strand fastq.gz file", action=AddOutputPrefix)
    out_group.add_argument("--output-single-fastq-gz",
                           help="Single reads fastq.gz file", action=AddOutputPrefix)

    return vars(parser.parse_args())


def exit_with_error(message: str):
    logger.critical(message)
    sys.exit(1)


def compress_fastq_file(file_path: str, compressed_file_path: str):
    logger.info(f"Compressing '{file_path}' with pigz...")
    try:
        with open(compressed_file_path, "w") as f_out:
            cmd = ["pigz", "-c", file_path]
            logger.info(f"Running the following command: '{' '.join(cmd)}'")
            subprocess.run(cmd, stdout=f_out)
            logger.info(f"Compressed '{file_path}' to '{compressed_file_path}' successfully.")
    except Exception as error:
        exit_with_error(f"Failed to compress '{file_path}': {error}")


def compress_existing_fastq_files(temp_output_mapping: dict) -> None:
    for temp_fastq, output_fastq_gz in temp_output_mapping.items():
        if check_file_exists(temp_fastq) and output_fastq_gz is not None:
            compress_fastq_file(temp_fastq, output_fastq_gz)
        elif check_file_exists(temp_fastq) and output_fastq_gz is None:
            exit_with_error(f"File '{temp_fastq}' is not empty, but output file name is not specified.")
        else:
            logger.info(f"File '{temp_fastq}' is empty or does not exist, skipping...")


def check_file_exists(filename: str):
    return os.path.exists(filename) and os.path.getsize(filename) > 0


def convert_sra_to_fastq(sra_id: str, ngc_key_file: Optional[str]) -> None:
    logger.info(f"Converting '{sra_id}.sra' to fastq file...")
    cmd = ["fasterq-dump", sra_id, "-e", str(cpu_count()), "-O", tempdir, "-x"]
    if ngc_key_file:
        cmd += ["--ngc", ngc_key_file]
    logger.info(f"Running the following command: '{' '.join(cmd)}'")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        exit_with_error(f"Failed to convert '{sra_id}.sra' to fastq file")
    logger.info(f"Successfully converted '{sra_id}.sra' to '.fastq' file(s)")


def validate_sra_file(sra_id: str, ngc_arg: List) -> subprocess.CompletedProcess:
    logger.info(f"Validating '{sra_id}' accession...")
    sra_file_path = os.path.join(tempdir, sra_id, f"{sra_id}.sra")
    cmd = ["vdb-validate", sra_file_path] + ngc_arg
    logger.info(f"Running the following command with subprocess.run: '{' '.join(cmd)}'")
    result = subprocess.run(cmd)
    return result


def download_sra_file(sra_id: str, ngc_key_file: Optional[str]) -> Optional[int]:
    ngc_arg = ["--ngc", ngc_key_file] if ngc_key_file else []
    for i in range(DOWNLOAD_SRA_CONNECTIONS):
        logger.info(f"Try #{i + 1}: downloading '{sra_id}' accession...")
        cmd = ["prefetch", sra_id] + ngc_arg + ["--max-size", "u"]
        logger.info(f"Running the following command with subprocess.run: '{' '.join(cmd)}'")
        subprocess.run(cmd)
        sra_download_check = validate_sra_file(sra_id, ngc_arg).returncode
        if sra_download_check == 0:
            logger.info(f"'{sra_id}' accession is downloaded successfully.")
            break
    return sra_download_check


def run(sra_id: str,
        ngc_key_file: Optional[str],
        output_forward_fastq_gz: Optional[str],
        output_reverse_fastq_gz: Optional[str],
        output_single_fastq_gz: Optional[str]) -> None:

    os.chdir(tempdir)
    download_sra_file(sra_id, ngc_key_file)
    convert_sra_to_fastq(sra_id, ngc_key_file)
    temp_output_mapping = {
        os.path.join(tempdir, f"{sra_id}_1.fastq"): output_forward_fastq_gz,
        os.path.join(tempdir, f"{sra_id}_2.fastq"): output_reverse_fastq_gz,
        os.path.join(tempdir, f"{sra_id}.fastq"): output_single_fastq_gz,
    }
    compress_existing_fastq_files(temp_output_mapping)


if __name__ == "__main__":
    set_logger(LOGGER_FORMAT)

    tempdir = os.environ.get("TEMPDIR", "/tmp")
    outprefix = os.environ.get("HOME", "")
    logger.info(f"TEMPDIR = '{tempdir}', OUTPREFIX = '{outprefix}'")

    args = parse_args()
    logger.info(f"Starting program with the folowing arguments: {args}")
    run(**args)
    logger.info("Run is completed successfully.")

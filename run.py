import os
import sys
import logging
import argparse
import subprocess
from multiprocessing import cpu_count
from typing import Optional

DOWNLOAD_SRA_CONNECTIONS = 8
LOGGER_FORMAT = (
    "%(asctime)s | %(name)s | line %(lineno)-3d | %(levelname)-8s | %(message)s"
)
logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and process SRA files")

    parser.add_argument("--sra-id", type=str, required=True, help="SRA id")
    parser.add_argument("--ngc-key-file", help="dbGaP access key file")
    parser.add_argument("--output-forward-fastq-gz", help="Forward strand fastq.gz file")
    parser.add_argument("--output-reverse-fastq-gz", help="Reverse strand fastq.gz file")
    parser.add_argument("--output-single-fastq-gz", help="Single reads fastq.gz file")

    return parser.parse_args()


def check_file_exists(filename: str) -> bool:
    return os.path.exists(filename) and os.path.getsize(filename) > 0


def compress_fastq_file(file_path: str, compressed_file_path: str) -> None:
    if not check_file_exists(file_path):
        logger.warning(f"File '{file_path}' does not exist or is empty, skipping.")
        return

    logger.info(f"Compressing '{file_path}' to '{compressed_file_path}'")
    subprocess.run(["pigz", "-c", file_path, "-o", compressed_file_path], check=True)


def run_command(cmd: list, check: bool = True, capture_output: bool = False):
    try:
        return subprocess.run(
            cmd, check=check, capture_output=capture_output, text=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Command '{' '.join(cmd)}' failed: {e}")
        sys.exit(1)


def download_sra_file(sra_id: str, ngc_key_file: Optional[str]) -> None:
    ngc_arg = ["--ngc", ngc_key_file] if ngc_key_file else []
    for i in range(DOWNLOAD_SRA_CONNECTIONS):
        logger.info(f"Attempt #{i+1} to download '{sra_id}'")
        run_command(["prefetch", sra_id] + ngc_arg + ["--max-size", "u"])


def validate_sra_file(sra_id: str, ngc_key_file: Optional[str]) -> None:
    sra_file_path = os.path.join("/tmp", f"{sra_id}.sra")
    ngc_arg = ["--ngc", ngc_key_file] if ngc_key_file else []
    run_command(["vdb-validate", sra_file_path] + ngc_arg)


def convert_sra_to_fastq(sra_id: str, ngc_key_file: Optional[str]) -> None:
    logger.info(f"Converting '{sra_id}.sra' to fastq")
    ngc_arg = ["--ngc", ngc_key_file] if ngc_key_file else []
    run_command(["fasterq-dump", sra_id, "-e", str(cpu_count()), "-O", "/tmp"] + ngc_arg)


def run(sra_id: str, ngc_key_file: Optional[str], output_forward_fastq_gz: Optional[str],
        output_reverse_fastq_gz: Optional[str], output_single_fastq_gz: Optional[str]) -> None:
    download_sra_file(sra_id, ngc_key_file)
    validate_sra_file(sra_id, ngc_key_file)
    convert_sra_to_fastq(sra_id, ngc_key_file)

    temp_output_mapping = {
        f"/tmp/{sra_id}_1.fastq": output_forward_fastq_gz,
        f"/tmp/{sra_id}_2.fastq": output_reverse_fastq_gz,
        f"/tmp/{sra_id}.fastq": output_single_fastq_gz,
    }

    for temp_fastq, output_fastq_gz in temp_output_mapping.items():
        if output_fastq_gz:
            compress_fastq_file(temp_fastq, output_fastq_gz)


if __name__ == "__main__":
    args = parse_args()
    run(args.sra_id, args.ngc_key_file, args.output_forward_fastq_gz,
        args.output_reverse_fastq_gz, args.output_single_fastq_gz)

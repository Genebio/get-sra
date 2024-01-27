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




if __name__ == "__main__":
    set_logger(LOGGER_FORMAT)

    tempdir = os.environ.get("TEMPDIR", "/tmp")
    outprefix = os.environ.get("HOME", "")
    logger.info(f"TEMPDIR = '{tempdir}', OUTPREFIX = '{outprefix}'")

    args = parse_args()
    logger.info(f"Starting program with the folowing arguments: {args}")
    run(**args)
    logger.info("Run is completed successfully.")

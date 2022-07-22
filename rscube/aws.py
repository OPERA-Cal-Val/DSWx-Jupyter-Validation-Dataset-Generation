"""Tools for working with AWS"""

import logging
from pathlib import Path
from tqdm import tqdm

import boto3
from boto3.s3.transfer import TransferConfig


S3_CLIENT = boto3.client('s3')

def upload_file_to_s3(path_to_file: Path, bucket: str, prefix: str = '') -> str:

    config = TransferConfig(multipart_threshold=1024,
                            max_concurrency=30,
                            # Commenting this out appears to make upload speed more variable
                            #multipart_chunksize=1024,
                            use_threads=True)


    key = str(Path(prefix) / path_to_file.name)
    S3_CLIENT.upload_file(str(path_to_file), bucket, key)
    return f'{bucket}/{key}'

def upload_directory_to_s3(path_to_directory: Path,
                           bucket: str,
                           prefix: str = '') -> list:

    paths = list(path_to_directory.glob('*'))
    paths = list(filter(lambda x: x.is_file(), paths))

    def upload_file_to_s3_p(path):
        return upload_file_to_s3(path, bucket, prefix=prefix)
    return list(map(upload_file_to_s3_p, tqdm(paths, desc='uploading files')))


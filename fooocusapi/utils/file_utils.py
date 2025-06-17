# -*- coding: utf-8 -*-

""" File utils

Use for managing generated files

@file: file_utils.py
@author: Konie
@update: 2024-03-22
"""
import base64
import datetime
import shutil
from io import BytesIO
import os
from pathlib import Path

import boto3
import numpy as np
from PIL import Image
from botocore.exceptions import NoCredentialsError, ClientError

from fooocusapi.utils.logger import logger
from fooocusapi.configs.config import infra_settings


output_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../..', 'outputs', 'files'))
os.makedirs(output_dir, exist_ok=True)

STATIC_SERVER_BASE = 'http://127.0.0.1:8888/files/'


def save_output_file(
        img: np.ndarray | str,
        image_name: str = '',
        extension: str = 'png') -> str:
    """
    Save np image to file
    Args:
        img: np.ndarray image to save
        image_name: str of image name
        extension: str of image extension
    Returns:
        str of file name
    """
    current_time = datetime.datetime.now()
    date_string = current_time.strftime("%Y-%m-%d")

    filename = os.path.join(date_string, image_name + '.' + extension)
    file_path = os.path.join(output_dir, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        if isinstance(img, str):
            shutil.move(img, file_path)
        return Path(file_path).as_posix()
    except Exception:
        raise Exception


def delete_output_file(filename: str):
    """
    Delete files specified in the output directory
    Args:
        filename: str of file name
    """
    file_path = os.path.join(output_dir, filename)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        logger.std_warn(f'[Fooocus API] {filename} not exists or is not a file')
    try:
        os.remove(file_path)
        logger.std_info(f'[Fooocus API] Delete output file: {filename}')
        return True
    except OSError:
        logger.std_error(f'[Fooocus API] Delete output file failed: {filename}')
        return False


def upload_to_minio(file_buffer: BytesIO, bucket_name: str, s3_key: str, content_type: str) -> str:
    """
    Загружает файл из памяти (BytesIO) в MinIO и возвращает URL.
    """
    s3_client = boto3.client(
        's3',
        endpoint_url='http://127.0.0.1:9001',
        aws_access_key_id=infra_settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=infra_settings.MINIO_SECRET_KEY,
    )

    try:
        s3_client.upload_fileobj(
            file_buffer,
            bucket_name,
            s3_key,
            ExtraArgs={'ContentType': content_type}
        )
        return f"http://127.0.0.1:9001/{s3_key}"
    except (NoCredentialsError, ClientError) as e:
        print(f"Ошибка при загрузке в MinIO: {e}")
        raise


def output_file_to_base64img(filename: str | None, upload_to_s3: bool = False, bucket_name: str = "fooocus") -> str | None:
    """
    Convert an image file to a base64 string.
    Args:
        filename: str of file name
    return: str of base64 string
    """
    if filename is None:
        return None
    file_path = os.path.join(output_dir, filename)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return None

    ext = filename.split('.')[-1]
    if ext.lower() not in ['png', 'jpg', 'webp', 'jpeg']:
        ext = 'png'

    try:
        img = Image.open(file_path)
        output_buffer = BytesIO()
        img.save(output_buffer, format=ext.upper())
        if upload_to_s3:
            output_buffer.seek(0)
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            base_name = filename.split('/')[-1]
            s3_key = f"{current_date}/{base_name}.{ext}"
            content_type = f"image/{ext}"
            return upload_to_minio(output_buffer, bucket_name, s3_key, content_type)
        else:
            byte_data = output_buffer.getvalue()
            base64_str = base64.b64encode(byte_data).decode('utf-8')
            return f"data:image/{ext};base64," + base64_str
    except Exception as e:
        return None


def output_file_to_bytesimg(filename: str | None) -> bytes | None:
    """
    Convert an image file to a bytes string.
    Args:
        filename: str of file name
    return: bytes of image data
    """
    if filename is None:
        return None
    file_path = os.path.join(output_dir, filename)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return None

    img = Image.open(file_path)
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    return byte_data


def get_file_serve_url(filename: str | None) -> str | None:
    """
    Get the static serve url of an image file.
    Args:
        filename: str of file name
    return: str of static serve url
    """
    if filename is None:
        return None
    return STATIC_SERVER_BASE + '/'.join(filename.split('/')[-2:])

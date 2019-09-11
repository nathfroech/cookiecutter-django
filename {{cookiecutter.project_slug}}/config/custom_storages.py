"""
Redefined AWS storages.

For more information see http://stackoverflow.com/questions/10390244/
Full-fledge class: https://stackoverflow.com/a/18046120/104731
"""

from storages.backends.s3boto3 import S3Boto3Storage


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = 'static'


class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

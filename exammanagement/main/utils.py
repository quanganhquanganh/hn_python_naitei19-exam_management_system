import boto3
from botocore.config import Config
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from main.models import Notification
from six import text_type


class S3:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.MEDIA_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version=settings.AWS_S3_SIGNATURE_NAME),
        )

    def get_presigned_url(self, key, bucket, time=3600):
        return self.client.generate_presigned_url(
            ClientMethod="put_object",
            ExpiresIn=time,
            Params={"Bucket": bucket, "Key": key},
        )

    def get_file(self, key, bucket, time=3600):
        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            ExpiresIn=time,
            Params={"Bucket": bucket, "Key": key},
        )

    def delete_file(self, key, bucket):
        return self.client.delete_object(Bucket=bucket, Key=key)


class AppTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return text_type(user.is_active) + text_type(user.pk) + text_type(timestamp)


def send_notification(user, content, url=None, updated_chapter=None):
    Notification.objects.create(
        user=user, content=content, url=url, updated_chapter=updated_chapter
    )


token_generator = AppTokenGenerator()

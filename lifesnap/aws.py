import base64
import boto3
import json
# import botocore


class AWS(object):
    """ Handle AWS S3 functions """

    def __init__(self, bucket_name: str):
        super()
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3')

    def upload_image(self, key_name: str, b64_bytes: str) -> str:
        """ upload an image to our S3 bucket
            key_name: this is the key name for the image being uploaded. This can be thought of as the files name
            b64_bytes: the frontend will need to encode the image to base64 per RFC 3548 this encoding is safe for HTTP POST this is what will be uploaded to our S3 bucket.

            return value: a string representing a URL that can be used do download the image or placed inside <image> tags to view
        """
        # key_name = user_id + post_id.png ???
        if not b64_bytes:
            raise ValueError('b64_bytes byte size is 0')

        b64_bytes = bytes(b64_bytes, encoding='utf-8')
        image_bytes = base64.b64decode(b64_bytes)

        self.s3.put_object(
            Body=image_bytes,
            Bucket=self.bucket_name,
            Key=key_name,
            ACL='public-read',
            ContentType='image/*',
            ServerSideEncryption='AES256'
        )

        url = self.s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': key_name
            }
        )
        return url[:url.find('?')]

    def remove_image(self, key_name: str):
        """ remove an image from our AWS S3 bucket
            key_name: the name of the image to delete, format user_id + post_id.png
        """
        # deleting from a S3 bucket will always return a 204. no solid way of checking success
        self.s3.delete_object(Bucket=self.bucket_name, Key=key_name)

    def remove_images(self, key_names: [str]):
        """ removes multiple images from our AWS S3 bucket
            key_names: list of the image names that need to be deleted.
        """
        if not key_names:
            return

        objects = []
        for key in key_names:
            objects.append({
                'Key': key
            })

        resp = self.s3.delete_objects(
            Bucket=self.bucket_name,
            Delete=dict({
                'Objects': objects,
            })
        )
        return resp

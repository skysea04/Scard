import boto3

s3 = boto3.client('s3')

with open('default_avatar.jpeg', 'rb') as f:
    s3.upload_fileobj(f, "scard-bucket", 'avatar/default_avatar.jpeg', ExtraArgs={'ContentType': "image/jpeg", 'ACL': "public-read"})

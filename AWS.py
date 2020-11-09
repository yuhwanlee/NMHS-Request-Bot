import boto3


class AWSFileManager:
    def __init__(self):
        self.s3 = boto3.client('s3', aws_access_key_id='--------',
                               aws_secret_access_key='--------')
        """for bucket in s3.buckets.all():  # for boto3.resource
            print(bucket)"""

    def download_unaccepted(self):
        with open('unaccepted_requests.csv', 'wb') as file:
            self.s3.download_fileobj('chsnmhs', 'aws_unaccepted_requests.csv', file)

    def upload_unaccepted(self):
        with open("unaccepted_requests.csv", 'rb') as file:
            self.s3.upload_fileobj(file, 'chsnmhs', 'aws_unaccepted_requests.csv')

    def download_accepted(self):
        with open('accepted_requests.csv', 'wb') as file:
            self.s3.download_fileobj('chsnmhs', 'aws_accepted_requests.csv', file)

    def upload_accepted(self):
        with open("accepted_requests.csv", 'rb') as file:
            self.s3.upload_fileobj(file, 'chsnmhs', 'aws_accepted_requests.csv')

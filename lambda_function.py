import boto3
import urllib.parse

glue = boto3.client('glue')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    print(f"New file in S3: s3://{bucket}/{key}")
   
    response = glue.start_job_run(
        JobName='Vehicle-stream',  
        Arguments={
            '--source_s3_path': f's3://{bucket}/{key}'
        }
    )

    print(f"Glue job started: JobRunId = {response['JobRunId']}")
    return {
        'statusCode': 200,
        'body': f"Triggered Glue job for s3://{bucket}/{key}"
    }


import json
import boto3
import os
import cv2
import argparse
from PIL import Image
import time
import io
from generate import generate

def setup_arg_parser():
    parser = argparse.ArgumentParser(description='Process images with S3 and SQS simulation.')
    parser.add_argument('--base_path', required=True, help='Pseudo name for bucket name')
    parser.add_argument('--image_path', required=True, help='image name')
    parser.add_argument('--prompt', required=True, help='image prompt')
    parser.add_argument('--aws', action='store_true', default=False, help='Enable AWS mode for operation.')
    parser.add_argument('--profile_name', default='', help='AWS profile name')
    parser.add_argument('--region_name', default='', help='AWS region name')
    parser.add_argument('--queue_name', default='', help='AWS queue name')
    return parser


def download_file_s3(s3, bucket_name, object_key, local_path):
    # Download the image file from S3
    s3_object = s3.Object(bucket_name, object_key)
    image_data = s3_object.get()['Body'].read()

    # Save the contents to a file
    with open(local_path, 'wb') as f:
        f.write(image_data)
            

def save_result(generated_image, args, base_path, image_path, s3=None):
    if args.aws and s3:
        # AWS Mode: Construct result_key for S3
        result_key = os.path.join(*(image_path.split("/")[:-1] + ["result.jpeg"]))
        buffer = io.BytesIO()
        generated_image.save(buffer, format='JPEG')
        buffer.seek(0)
        
        # Upload to S3
        s3.Bucket(base_path).put_object(
            Body=buffer.getvalue(),
            Key=result_key,
            ContentType='image/jpeg'
        )
        buffer.close()
        return True
    else:
        # Local Mode: Construct local file save path
        result_path = os.path.join(base_path, "result.jpeg")
        if isinstance(generated_image, Image.Image):
            # Ensure the directory exists
            # os.makedirs(os.path.dirname(result_path), exist_ok=True)
            generated_image.save(result_path)



# AWS needs to be set up before hand or we can pass the accound details as an environment variable too
def main(args):   
    if args.aws:
        profile_name = args.profile_name
        region_name = args.region_name
        queue_name = args.queue_name
        session = boto3.session.Session(profile_name = profile_name)
        sqs = session.resource('sqs', region_name = region_name)
        s3 = session.resource('s3', region_name = region_name)
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        while True:
            msg_received = queue.receive_messages(MessageAttributeNames=['All'], MaxNumberOfMessages=1, WaitTimeSeconds=10)
            
            if msg_received:
                for message in msg_received:
                    # the body can include the bucket name where an uploaded image is stored, the object path in that bucket (other optional fields could be added too like "prompt")  
                    msg_body = json.loads(message.body)
                    bucket_name = msg_body['bucket_name']
                    object_key = msg_body['object_key']
                    prompt = msg_body.get('prompt', "photo of a person")  # Providing default prompt
                    local_path = os.path.join("/tmp", object_key.split('/')[-1])  # Using /tmp for lambda or ephemeral storage
                    download_file_s3(s3, bucket_name, object_key, local_path)
                    generated_image = generate(local_path, prompt)
                    response = save_result(generated_image, args, bucket_name, object_key, s3)
                    if response:
                        message.delete()

            else:
                time.sleep(5)
    else:
        base_path = args.base_path  # Directory where the image resides
        image_path = args.image_path  # Image name
        prompt = args.prompt
        local_path = os.path.join(base_path, image_path)  # Full path to the image
        generated_image = generate(local_path, prompt)
        save_result(generated_image, args, base_path, image_path)
        
if __name__ == "__main__":
    parser = setup_arg_parser()
    args = parser.parse_args()
    main(args)

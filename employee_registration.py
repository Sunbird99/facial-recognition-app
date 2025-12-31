import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodbTableName = 'employees'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
employeesTable = dynamodb.Table(dynamodbTableName)

#takes images from bucket and registers faces as employees
def lambda_handler(event, context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    try:
        response = index_employees_image(bucket, key)
        print(response)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId = response['FaceRecords'][0]['Face']['FaceId']
            name = key.split('.')[0].split('_')
            firstName = name[0]
            lastName = name[1]
            register_employee(faceId, firstName, lastName)
        return response
    except Exception as e:
        print(e)
        print('Error processing employee image {} from bucket{}.'.format(key, bucket))
        raise e

#indexes employees    
def index_employees_image(bucket, key):
    response = rekognition.index_faces(
        Image={
            'S3Object':
            {
                'Bucket': bucket,
                'Name': key
            }
        },
        CollectionId='employees'
    )
    return response

#registers employees
def register_employee(faceId, firstName, lastName):
    employeesTable.put_item(
        Item={
            'rekognitionId': faceId,
            'firstName':firstName,
            'lastName': lastName
        }
    )
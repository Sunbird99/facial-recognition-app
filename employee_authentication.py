import boto3
import json

#sets up the s3 bucket, rekognition service, and dynamo table
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodbTableName = 'employees'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
employeesTable = dynamodb.Table(dynamodbTableName)
bucketName = 'jnvisitor-facial-images'

#uses the rekognition service to filter and authenticate the faces from the visitor s3 bucket 
def lambda_handler(event, context):
    print(event)
    objectKey = event['queryStringParameters']['objectKey']
    image_bytes = s3.get_object(Bucket=bucketName, Key=objectKey)['Body'].read()
    response = rekognition.search_faces_by_image(
        CollectionId='employees',
        Image={'Bytes':image_bytes}
    )

    for match in response['FaceMatches']:
        print(match['Face']['FaceId'], match['Face']['Confidence'])

        face = employeesTable.get_item(
            Key={
                'rekognitionId': match['Face']['FaceId']
            }
        )

        if 'Item' in face:
            print('Person was Found: ', face['Item'])
            return buildResponse(200, {
                'Message': 'Success',
                'firstName': face['Item']['firstName'],
                'lastName': face['Item']['lastName']
            })
    print('Person could not be recognized.')
    return buildResponse(403, {'Message': 'Person was not Found'})

#returns http responses based on what pictures the lambda handler function recognizes
def buildResponse(statusCode, body=None):
    
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

    if body is not None:
        response['body'] = json.dumps(body)
    return response
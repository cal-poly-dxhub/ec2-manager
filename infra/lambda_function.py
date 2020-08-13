import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AMI = 'ami-09dbb0b2eb0209c2d'
INSTANCE_SIZE = 't3a.micro'
SG = 'ssh-world'
PROFILE = 'ec2-update-route53'
S3 = 'calpoly-cpe453-keys'

# Functions called from API Gateway will have the event variable set as follows
# see sample_event.json

def ec2_manager_handler(event, context):
    logger.info('event{}'.format(event))
    statusCode = 200

    retval = {
        "isBase64Encoded": 'false',
        "statusCode": '503',
        "headers": {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "headerName": "headerValue",

        },

    }
# Get all variables needed for processing
#  We need user and service name for determining
#   which instance to operate on
# Event object should contain both

# Action

    # Which path did we get from API Gateway indicating the method to execute?
    try:
        pathParameters = event['pathParameters']
        action = pathParameters['proxy']
        logger.info(action)
    except KeyError:
        logger.error("Missing action in event")
        retval['body'] = '{"result":"Missing action in event"}'
        return retval

# Service
    try:
        if event['queryStringParameters']:
            ami = event['queryStringParameters']['ami']
        else:
            ami = AMI
        logger.info(ami)
    except KeyError:
        logger.error("Missing AMI name in event")
        ami = AMI
# User
    try:
        user = event['requestContext']['authorizer']['claims']['cognito:username']
        logger.info("Checking username")
        logger.info(user)
    except KeyError:
        logger.error("Missing username in event")
        retval['body'] = '{"result":"Missing cofgnito username in event"}'
        return retval
# Instance in the case user has more than one
    try:
        if event['queryStringParameters']:
            instanceId = event['queryStringParameters']['instanceId']
        else:
            instanceId = "all"
    except KeyError:
        instanceId = "all"

    if action == "list":
        return list_instances(user)
    elif action == "stop":
        return stop_instances(user)
    elif action == "start":
        return start_instances(user, instanceId)
    elif action == "create":
        return create_instances(user, ami)
    elif action == "terminate":
        return terminate_instances(user)
    elif action == "get-key":
        return get_key(user)
    else:
        return retval


def stop_instances(user):
    ec2 = boto3.resource('ec2')
    logger.info('Checking for instances to stop for %s', user)

    userFilter = "{\"Name\": \"tag:Name\", \"Values\": [\"" + user + "\"]}"
    stateFilter = "{\"Name\": \"instance-state-name\", \"Values\": [\"running\"]}"


    filters = []
    filters.append(json.loads(userFilter))
    filters.append(json.loads(stateFilter))
    logger.info(filters)

    instances = ec2.instances.filter(Filters=filters)

    runningInstances = [instance.id for instance in instances]

    instanceData = "{\"result\":"
    i = 0
    for instance in instances:
        if i > 0:
            instanceData = instanceData + ","
        instanceData = instanceData + "{\"InstanceId\": \"" + str(instance.id) + "\"}"
        i = i + 1
    instanceData = instanceData + "}"

    retval = {
        "isBase64Encoded": 'false',
        "statusCode": '200',
        "headers": {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Date,X-Amzn-Trace-Id,x-amz-apigw-id,x-amzn-RequestId",
        },

    }

    if len(runningInstances) > 0:
        shuttingDown = ec2.instances.filter(InstanceIds=runningInstances).stop()
        logger.info('Found instance to stop %s ', runningInstances)
        retval['body'] = instanceData
    else:
        logger.info('Nothing to stop')
        retval['body'] = '{"result":{"InstanceId": "nothing to stop"}}'



    logger.info('Returning{}'.format(retval))

    return retval;

def get_key(user):
    s3 = boto3.client('s3', region_name='us-west-2')
    
    obj = s3.get_object(Bucket=S3, Key=user)
    unformatted_key = str(obj['Body'].read())
    # replace \n with html break to format string for browser
    #unformatted_key = unformatted_key.replace('\\n', '<br />')
    # remove first 2 chars and last single quote
    unformatted_key = unformatted_key[2:-1]
    
    keyValue = "{\"result\":"
    keyValue = keyValue + "{\"key\": \"" + unformatted_key + "\"}}"
    
    retval = {
        "isBase64Encoded": 'false',
        "statusCode": '200',
        "headers": {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Date,X-Amzn-Trace-Id,x-amz-apigw-id,x-amzn-RequestId",
        },
    
    }
    retval['body'] = keyValue
    
    logger.info(retval)
    
    return retval;

def start_instances(user, instanceId):
    ec2 = boto3.resource('ec2')
    logger.info('Checking for instances to start for %s', user)

    filters = []

    userFilter = "{\"Name\": \"tag:Name\", \"Values\": [\"" + user + "\"]}"
    stateFilter = "{\"Name\": \"instance-state-name\", \"Values\": [\"stopped\"]}"

    if instanceId != "all":
        instanceFilter =  "{\"Name\": \"instance-id\", \"Values\": [\"" + instanceId + "\"]}"
        filters.append(json.loads(instanceFilter))


    filters.append(json.loads(userFilter))
    filters.append(json.loads(stateFilter))
    logger.info(filters)

    instances = ec2.instances.filter(Filters=filters)

    stoppedInstances = [instance.id for instance in instances]

    instanceData = "{\"result\":"
    i = 0
    for instance in instances:
        if i > 0:
            instanceData = instanceData + ","
        instanceData = instanceData + "{\"InstanceId\": \"" + str(instance.id) + "\"}"
        i = i + 1
    instanceData = instanceData + "}"

    retval = {
        "isBase64Encoded": 'false',
        "statusCode": '200',
        "headers": {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Date,X-Amzn-Trace-Id,x-amz-apigw-id,x-amzn-RequestId",
        },

    }

    if len(stoppedInstances) > 0:
        startingInstances = ec2.instances.filter(InstanceIds=stoppedInstances).start()
        logger.info('Found instance to start %s ', startingInstances)
        retval['body'] = instanceData
    else:
        logger.info('Nothing to start')
        retval['body'] = '{"result":{"InstanceId": "nothing to start"}}'



    logger.info('Returning{}'.format(retval))

    return retval;
    
def create_instances(user, ami):
    
    ec2 = boto3.resource('ec2')
    logger.info('Getting ready to create instance for %s', user)
    
    filters = []
    
    userFilter = "{\"Name\": \"tag:Name\", \"Values\": [\"" + user + "\"]}"
    notTerminated="{\"Name\": \"instance-state-name\", \"Values\": [\"running\",\"stopped\",\"stopping\",\"shutting-down\",\"pending\"]}"
    
    filters.append(json.loads(userFilter))
    filters.append(json.loads(notTerminated))
    logger.info(filters)
    
    # Check to see if this user has an instance?
    instances = ec2.instances.filter(Filters=filters)
    
    totalInstances = [instance.id for instance in instances]
    logger.info("User has %d instances:", len(totalInstances))
    
    #okay to start instance since use doesn't have any
    created_instances = {}
    if len(totalInstances) == 0:
        #checks to make sure user has a key to start instance
        create_key(user)
    
        newinstances = ec2.create_instances(
         ImageId=ami,
         MinCount=1,
         MaxCount=1,
         InstanceType=INSTANCE_SIZE,
         KeyName=user,
         SecurityGroupIds=[SG],
         TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [{
                         'Key': 'Name',
                        'Value': user
                    }]
                }
            ],
            IamInstanceProfile={
            'Name': PROFILE
            },
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'VolumeSize': 10,
                        'VolumeType': 'gp2'
                    }
                }
            ]
        )
        logger.info(newinstances)
    
        created_instances = [instance.id for instance in newinstances]
    
        instanceData = "{\"result\":"
        i = 0
        for instance in newinstances:
            if i > 0:
                instanceData = instanceData + ","
            instanceData = instanceData + "{\"InstanceId\": \"" + str(instance.id) + "\"}"
            i = i + 1
        instanceData = instanceData + "}"
     
    retval = {
        "isBase64Encoded": 'false',
        "statusCode": '200',
        "headers": {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Date,X-Amzn-Trace-Id,x-amz-apigw-id,x-amzn-RequestId",
        },
    
    }
    
    if len(created_instances) > 0:
        logger.info('Created instance %s ', created_instances)
        retval['body'] = instanceData
    else:
        logger.info('Nothing to start')
        retval['body'] = '{"result":{"InstanceId": "Nothing to start user already has an instance"}}'
    
    logger.info('Returning{}'.format(retval))

    return retval;
    
def create_key(user):
    # Check to see this user has a key generated
    ec2 = boto3.client('ec2')
    response = ec2.describe_key_pairs()
    keyPairs = response['KeyPairs']
    
    createkey = True
    for key in keyPairs:
        logger.info("Checking keys for user %s", user)
        logger.info(key['KeyName'])
        # user key found no need to create
        if key['KeyName']==user:   
            createkey = False
            break
        
    if createkey:
        response = ec2.create_key_pair(KeyName=user)
    
        s3 = boto3.client('s3')
        bucket = S3
        key = user
        id = None
        logger.info("Bucket %s, Key=%s", bucket, key)
        # Write id to S3
        id = s3.put_object(Body=response['KeyMaterial'], Bucket=bucket, Key=key)
        #print(id)


def list_instances(user):
    ec2 = boto3.resource('ec2')
    logger.info('Attempting to list instances')
    
    userFilter = "{\"Name\": \"tag:Name\", \"Values\": [\"" + user + "\"]}"
    logger.info(userFilter)
    
    filters = []
    filters.append(json.loads(userFilter))
    
    instances = ec2.instances.filter(Filters=filters)
    
    instanceData = "{\"result\":["
    i = 0
    for instance in instances:
        public_dns=instance.public_dns_name
        if public_dns == '':
            public_dns='None'
        if i > 0:
            instanceData = instanceData + ","
        instanceData = instanceData + "{\"InstanceId\": \"" + str(instance.id) + "\", \"State\": \"" + str(instance.state['Name']) + "\", \"Public_DNS\": \"" + str(public_dns) + "\", \"Public_IP\": \"" + str(instance.public_ip_address) + "\"}"
        i = i + 1
        logger.info("Atteributes of your instance DNS=%s, ID=%s, STATE=%s, IP=%s", public_dns, instance.id, instance.state['Name'], instance.public_ip_address)
    instanceData = instanceData + "]}"
    
    logger.info(instanceData)
    
    retval = {
        "isBase64Encoded": 'false',
         "statusCode": '200',
        "headers": {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Date,X-Amzn-Trace-Id,x-amz-apigw-id,x-amzn-RequestId",
        },
    
    }
    if i > 0:
        retval['body'] = instanceData
    else:
        no_instances = {
            "result":[
                {
                    "InstanceId": "None", 
                    "State": "None", 
                    "Public_DNS":"None", 
                    "Public_IP": "None"
                }
            ]
        }
        retval['body'] = json.dumps(no_instances)
    logger.info(retval)
    return retval;
    
def terminate_instances(user):
    ec2 = boto3.resource('ec2')
    logger.info('Checking for instances to terminate for %s', user)

    userFilter = "{\"Name\": \"tag:Name\", \"Values\": [\"" + user + "\"]}"
    notTerminated="{\"Name\": \"instance-state-name\", \"Values\": [\"running\",\"stopped\",\"stopping\",\"shutting-down\",\"pending\"]}"


    filters = []
    filters.append(json.loads(userFilter))
    filters.append(json.loads(notTerminated))

    logger.info(filters)

    instances = ec2.instances.filter(Filters=filters)

    runningInstances = [instance.id for instance in instances]

    instanceData = "{\"result\":"
    i = 0
    for instance in instances:
        if i > 0:
            instanceData = instanceData + ","
        instanceData = instanceData + "{\"InstanceId\": \"" + str(instance.id) + "\"}"
        i = i + 1
    instanceData = instanceData + "}"

    retval = {
        "isBase64Encoded": 'false',
        "statusCode": '200',
        "headers": {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Date,X-Amzn-Trace-Id,x-amz-apigw-id,x-amzn-RequestId",
        },

    }

    if len(runningInstances) > 0:
        shuttingDown = ec2.instances.filter(InstanceIds=runningInstances).terminate()
        logger.info('Found instance to terminate %s ', runningInstances)
        retval['body'] = instanceData
    else:
        logger.info('Nothing to stop')
        retval['body'] = '{"result":{"InstanceId": "Nothign to terminate"}}'


    logger.info('Returning{}'.format(retval))
    return retval;
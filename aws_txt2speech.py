import boto3
import time
import sys


print("Hello World!")


try:
    f = open("input.txt", "r")
    lines= f.readlines()
    txt="".join(lines)
except :
    if not sys.stdin.isatty():
        print("reading from stdin")
        txt = sys.stdin.read()
    else:
        print("To use the program please paste text into .input.txt or use a pipe")
        print("exiting....")
        sys.exit()


##
# make sure to config "~/.aws/config" and "~/.aws/credentials"

#polly_client = boto3.Session(aws_access_key_id='',aws_secret_access_key='', region_name='eu-north-1').client('polly')
polly_client = boto3.Session().client('polly')

time.sleep(0.8)
response = polly_client.start_speech_synthesis_task(VoiceId='Brian',
                OutputS3BucketName='mytest9752635',
                OutputS3KeyPrefix='5a4365a713a9a28144cae362e50fceed47dab84db405a5c7d4a6b216176ac50d',
                OutputFormat='pcm', 
                Text = txt)



OutputUri = response['SynthesisTask']['OutputUri']
taskId =    response['SynthesisTask']['TaskId']
objectName=OutputUri.split("/")[-1]
print(taskId)
current_task_status=''
while(current_task_status != 'completed'):
    print("waiting for rendering ...")
    task_status = polly_client.get_speech_synthesis_task(TaskId = taskId)
    time.sleep(0.8)
    current_task_status=task_status['SynthesisTask']['TaskStatus']
    print(current_task_status)
    time.sleep(0.8)


#s3 =  boto3.client('s3',aws_access_key_id='',aws_secret_access_key='')
s3 = boto3.client('s3')
print("Downloading...")
s3.download_file('mytest9752635',objectName,'out.wav')
time.sleep(2)
print("Deleting s3 object...")
s3.delete_object(Bucket='mytest9752635',Key=objectName)

os.system("aplay -r 16000 out.wav ") 
os.system("rm out.wav ") 

    
    
    

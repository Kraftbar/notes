# aws-r


 ### Make sure to configure AWS



>   ```sh
> mkdir ~/.aws/
> touch ~/.aws/config
> touch ~/.aws/credentials
>   ```


 ~/.aws/config
```
[default]
region=eu-north-1
```

Generate aws_access_key_id and aws_secret_access_key
- Go to your AWS account overview           
- Account menu in the upper-right (has your name on it)         
- sub-menu: Security Credentials           


~/.aws/credentials
```
credentials
[default]
aws_access_key_id=YOUR_AWS_ACCESS_KEY_ID
aws_secret_access_key=YOUR_AWS_SECRET_ACCESS_KEY
```












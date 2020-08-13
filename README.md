# EC2 Manager
This React based application uses Cognito, API Gateway and a Lambda function to allow users to create one and only one EC2 instance. The application allows them to start, stop and terminate that instance as well as dynmically creates a public/private key pair so they can SSH into the instance.  This code was used for a computer science operating systems class to have a virtual lab environment during remote instruction.

# webapp
This folder contains the React App used by students.  

**npm install** to pull in packages needed by the web app

**npm run**

# infra
This folder contains the lambda funtion that accompanies the React App.

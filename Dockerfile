FROM public.ecr.aws/lambda/python:3.9

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy your application code
COPY . ${LAMBDA_TASK_ROOT}

# Set the working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Command to run the Lambda function handler
CMD ["lambda_function.lambda_handler"]

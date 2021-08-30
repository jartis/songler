# Set base image (host OS)
FROM python

# By default, listen on port 5000
EXPOSE 5000/tcp
EXPOSE 80

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY app.py .
COPY serve.py .
COPY templates ./templates/
COPY static ./static/

#### TAKE THIS OUT FOR RELEASE ####
COPY dbconf.py .
#### TAKE THIS OUT FOR RELEASE ####

# Specify the command to run on container start
CMD [ "python", "./serve.py" ]
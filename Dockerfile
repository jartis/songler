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
COPY api.py .
COPY app.py .
COPY auth.py .
COPY conf.py .
COPY dbutil.py .
COPY nightbot.py .
COPY routes.py .
COPY serve.py .
COPY util.py .
COPY templates ./templates/
COPY static ./static/

# Specify the command to run on container start
CMD [ "python", "./serve.py" ]
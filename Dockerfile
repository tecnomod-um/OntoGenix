# Use an official Python runtime as the base image
FROM python:3.11.2

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the local package directories to the container's workspace.
COPY . .

# Install any needed Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define the command to run on container start
CMD [ "python", "./pipeline.py" ] 

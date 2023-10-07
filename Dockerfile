FROM python:3.11.3

WORKDIR /usr/src/app

ADD . ./

# RUN pip install --upgrade pip

# RUN pip install --no-cache-dir -r requirements.txt

# CMD [ "python", "./pipeline.py" ] 

# docker run -v `pwd`/data:/data ontogenix ./cmd.sh a
CMD [ "cmd.sh" , "x" ] 


# set base image (host OS)
FROM python:3.8-slim

# --- NETFREE CERT INTSALL ---
# ADD https://netfree.link/dl/unix-ca.sh /home/netfree-unix-ca.sh 
# RUN cat  /home/netfree-unix-ca.sh | sh
# ENV NODE_EXTRA_CA_CERTS=/etc/ca-bundle.crt
# ENV REQUESTS_CA_BUNDLE=/etc/ca-bundle.crt
# ENV SSL_CERT_FILE=/etc/ca-bundle.crt
# --- END NETFREE CERT INTSALL ---

# set the working directory in the container
WORKDIR /code
#ENV
ENV ROOM_FILES_PATH="./rooms/"
ENV CSV_PATH users.csv
ENV FLASK_ENV development
# copy the dependencies file to the working directory
COPY requirements.txt .
# install dependencies
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt --no-cache-dir
# command to run on container start
CMD [ "python", "./chatApp.py" ]
# copy the content of the local src directory to the working directory
COPY . .




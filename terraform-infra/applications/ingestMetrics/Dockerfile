FROM demisto/boto3py3:1.0.0.86713

WORKDIR /usr/src

COPY startup.py /usr/src/startup.py

RUN chmod +x /usr/src/startup.py

ENTRYPOINT [ "python3", "/usr/src/startup.py" ]

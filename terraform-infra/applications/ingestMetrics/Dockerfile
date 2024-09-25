FROM public.ecr.aws/lambda/python:3.9

WORKDIR /usr/src

COPY startup.py /usr/src/startup.py

RUN chmod +x /usr/src/startup.py

ENTRYPOINT [ "python3", "/usr/src/startup.py" ]

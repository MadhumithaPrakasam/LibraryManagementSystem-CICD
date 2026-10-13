FROM python:3.12-slim

RUN pip install --no-cache-dir ansible-core docker

RUN ansible-galaxy collection install community.docker

WORKDIR /workspace

CMD ["ansible-playbook", "--version"]
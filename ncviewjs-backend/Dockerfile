FROM mambaorg/micromamba:1.0.0

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set working directory
WORKDIR /usr/src/ncviewjs-backend


COPY --chown=$MAMBA_USER:$MAMBA_USER ./envs/environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml
RUN micromamba clean --all -f -y

ARG MAMBA_DOCKERFILE_ACTIVATE=1

# copy project
COPY --chown=$MAMBA_USER:$MAMBA_USER . .

# add entrypoint.sh
COPY --chown=$MAMBA_USER:$MAMBA_USER ./entrypoint.sh .
RUN chmod +x /usr/src/ncviewjs-backend/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["/usr/src/ncviewjs-backend/entrypoint.sh"]

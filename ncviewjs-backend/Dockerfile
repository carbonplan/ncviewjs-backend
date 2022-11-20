# bring in the micromamba image so we can copy files from it
FROM mambaorg/micromamba:1.0.0 as micromamba

# This is the image we are going add micromamba to:
FROM debian:bullseye-slim


# install system dependencies
RUN apt-get update \
    && apt-get -y install netcat ca-certificates \
    && apt-get clean

ARG MAMBA_USER=mamba
ARG MAMBA_USER_ID=1000
ARG MAMBA_USER_GID=1000
ENV MAMBA_USER=$MAMBA_USER
ENV MAMBA_ROOT_PREFIX="/opt/conda"
ENV MAMBA_EXE="/bin/micromamba"

COPY --from=micromamba "$MAMBA_EXE" "$MAMBA_EXE"
COPY --from=micromamba /usr/local/bin/_activate_current_env.sh /usr/local/bin/_activate_current_env.sh
COPY --from=micromamba /usr/local/bin/_dockerfile_shell.sh /usr/local/bin/_dockerfile_shell.sh
COPY --from=micromamba /usr/local/bin/_entrypoint.sh /usr/local/bin/_entrypoint.sh
COPY --from=micromamba /usr/local/bin/_activate_current_env.sh /usr/local/bin/_activate_current_env.sh
COPY --from=micromamba /usr/local/bin/_dockerfile_initialize_user_accounts.sh /usr/local/bin/_dockerfile_initialize_user_accounts.sh
COPY --from=micromamba /usr/local/bin/_dockerfile_setup_root_prefix.sh /usr/local/bin/_dockerfile_setup_root_prefix.sh

RUN /usr/local/bin/_dockerfile_initialize_user_accounts.sh && \
    /usr/local/bin/_dockerfile_setup_root_prefix.sh

USER $MAMBA_USER

SHELL ["/usr/local/bin/_dockerfile_shell.sh"]


# You can modify the CMD statement as needed....
CMD ["/bin/bash"]



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
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "/usr/src/ncviewjs-backend/entrypoint.sh"]

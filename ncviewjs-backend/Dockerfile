
# bring in the micromamba image so we can copy files from it
FROM mambaorg/micromamba:1.1.0 as micromamba

# This is the image we are going add micromamba to:
FROM debian:bullseye-slim

ARG MAMBA_USER=mamba
ARG MAMBA_USER_ID=1000
ARG MAMBA_USER_GID=1000
ENV MAMBA_USER=$MAMBA_USER
ENV MAMBA_ROOT_PREFIX="/opt/conda"
ENV MAMBA_EXE="/bin/micromamba"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# modify the PATH at build-time to approximate an activated environment during docker exec
# warning - not a prefered method, but it works
ENV PATH "$MAMBA_ROOT_PREFIX/bin:$PATH"


COPY --from=micromamba "$MAMBA_EXE" "$MAMBA_EXE"
COPY --from=micromamba /usr/local/bin/_activate_current_env.sh /usr/local/bin/_activate_current_env.sh
COPY --from=micromamba /usr/local/bin/_dockerfile_shell.sh /usr/local/bin/_dockerfile_shell.sh
COPY --from=micromamba /usr/local/bin/_entrypoint.sh /usr/local/bin/_entrypoint.sh
COPY --from=micromamba /usr/local/bin/_activate_current_env.sh /usr/local/bin/_activate_current_env.sh
COPY --from=micromamba /usr/local/bin/_dockerfile_initialize_user_accounts.sh /usr/local/bin/_dockerfile_initialize_user_accounts.sh
COPY --from=micromamba /usr/local/bin/_dockerfile_setup_root_prefix.sh /usr/local/bin/_dockerfile_setup_root_prefix.sh

RUN /usr/local/bin/_dockerfile_initialize_user_accounts.sh && \
    /usr/local/bin/_dockerfile_setup_root_prefix.sh


# install system dependencies
RUN apt-get update \
    && apt-get -y install netcat ca-certificates \
    && apt-get clean

USER $MAMBA_USER

# You can modify the CMD statement as needed....
CMD ["/bin/bash"]

# set working directory
WORKDIR /home/$MAMBA_USER
# add entrypoint.sh
COPY --chown=$MAMBA_USER:$MAMBA_USER ./entrypoint.sh .
RUN chmod +x /home/${MAMBA_USER}/entrypoint.sh


# copy project
COPY . .

COPY ./envs/environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml
RUN micromamba clean --all -f -y

SHELL ["/usr/local/bin/_dockerfile_shell.sh"]

# run entrypoint.sh
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "/home/mamba/entrypoint.sh"]

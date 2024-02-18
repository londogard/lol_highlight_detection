FROM mcr.microsoft.com/vscode/devcontainers/miniconda:latest

USER vscode

COPY --chown=vscode . /app
WORKDIR /app

RUN conda env create -f env.yml
RUN conda clean -a -y
RUN conda init

EXPOSE 8765

ENV PATH /opt/conda/envs/highlights/bin/:$PATH

CMD ["solara", "run", "sol_app.py", "--host=0.0.0.0"]

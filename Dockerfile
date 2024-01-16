FROM mcr.microsoft.com/vscode/devcontainers/miniconda:latest

COPY env.yml .
RUN conda env create -f env.yml
RUN conda clean -a -y

EXPOSE 8765

COPY . /app
WORKDIR /app

RUN conda init
RUN echo "source activate highlights" > ~/.bashrc
ENV PATH /opt/conda/envs/highlights/bin:$PATH

CMD solara run sol_app.py --host=0.0.0.0
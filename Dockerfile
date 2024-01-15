FROM mcr.microsoft.com/vscode/devcontainers/miniconda:latest

COPY env.yml .
RUN conda env create -f env.yml -n
RUN conda clean -a -y

EXPOSE 8765

COPY . /app

RUN conda init
CMD conda run -n highlights solara run app/sol_app.py --host=0.0.0.0 --production
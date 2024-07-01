# DockerHubのイメージ
FROM python:3.12.4-slim
# 作業ディレクトリの指定
WORKDIR /workspace

# 必要なパッケージをインストール
RUN pip install poetry && poetry config virtualenvs.create false

# 環境変数
ENV PYTHONPATH=/workspace/scripts

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install

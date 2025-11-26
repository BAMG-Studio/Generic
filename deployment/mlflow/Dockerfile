# MLflow with PostgreSQL support
FROM ghcr.io/mlflow/mlflow:v3.6.0

# Install PostgreSQL driver and AWS SDK
RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.9 \
    boto3==1.34.0

# Expose MLflow port
EXPOSE 5050

# Run MLflow server (command will be provided by docker-compose)
ENTRYPOINT ["mlflow"]

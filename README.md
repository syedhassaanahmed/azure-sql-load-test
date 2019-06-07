# azure-sql-load-test
[![Docker Build Status](https://img.shields.io/docker/cloud/build/syedhassaanahmed/azure-sql-load-test.svg?logo=docker)](https://hub.docker.com/r/syedhassaanahmed/azure-sql-load-test/builds/) [![MicroBadger Size](https://img.shields.io/microbadger/image-size/syedhassaanahmed/azure-sql-load-test.svg?logo=docker)](https://hub.docker.com/r/syedhassaanahmed/azure-sql-load-test/tags/) [![Docker Pulls](https://img.shields.io/docker/pulls/syedhassaanahmed/azure-sql-load-test.svg?logo=docker)](https://hub.docker.com/r/syedhassaanahmed/azure-sql-load-test/)

This tool enables containerized load testing of Azure SQL Database and Azure SQL Data Warehouse by executing SQL queries from Docker containers. The SQL query is kept outside and is exposed to the tool as an online Python script (configured by `QUERY_SCRIPT_URL`). The script must contain a function `get_query()` which returns the SQL query. Having a function allows us to randomize aspects of the query. [Here](https://gist.githubusercontent.com/syedhassaanahmed/4a719feb5f496d672a040891c7ea51df/raw/ce38a1c71e7781595097f48c8ad35ccad726d897/sql_query.py) is an example Python script.

In order to measure E2E query latency, an optional [Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview) instrumentation can also be provided via `APPINSIGHTS_INSTRUMENTATIONKEY`.

## Configuration
```
CONNECTION_STRING=Driver={ODBC Driver 17 for SQL Server};Server=tcp:<SERVER_NAME>.database.windows.net,1433;Database=<DATABASE_NAME>;Uid=<USER_NAME>;Pwd=<PASSWORD>;
QUERY_SCRIPT_URL=https://.../query.py
TEST_ID=my_stressful_test
APPINSIGHTS_INSTRUMENTATIONKEY=<APPINSIGHTS_INSTRUMENTATIONKEY>
QUERIES_TOTAL=100
```

- If `TEST_ID` is not provided, a guid will be generated.
- Application Insights instrumentation will be ignored if `APPINSIGHTS_INSTRUMENTATIONKEY` is not provided.
- The tool will run indefinitely if `QUERIES_TOTAL` is not provided.

## Run Test
### Single Instance
Create a `.env` file with above configuration, then run;
```
docker run -it --rm --env-file .env syedhassaanahmed/azure-sql-load-test
```

### Concurrent
Generating concurrent load requires a Kubernetes (k8s) cluster. Here are some of the options to create a cluster;
- Use the [in-built Kubernetes](https://docs.docker.com/docker-for-windows/kubernetes/) in Docker Desktop for Windows.
- Install [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/).
- Create an [AKS](https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough) cluster in Azure.

Once the k8s cluster is up and running, modify the above environment variables in `deployment.yaml` file and run the following;
```
kubectl apply -f deployment.yaml
```

Logs from a successfully running deployment can be viewed by;
```
kubectl logs -l app=sql-load-test
```

To stop the load tests;
```
kubectl delete deployment sql-load-test
```

## Query Performance
E2E duration of all completed queries in Application Insights.
```sql
customMetrics
| where name == "query_time" and customDimensions.test_id == "my_stressful_test"
| summarize percentiles(value, 5, 50, 95) by bin(timestamp, 1m)
| render timechart
```
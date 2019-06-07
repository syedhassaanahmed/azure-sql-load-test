import os, uuid, timeit, functools, pyodbc

from query import get_query
from applicationinsights import TelemetryClient

######################################################
##                        AUTH                      ##
######################################################
connection_string = os.environ.get("CONNECTION_STRING")
cnxn = pyodbc.connect(connection_string)
cursor = cnxn.cursor()

######################################################
##                       QUERY                      ##
######################################################

test_id = os.environ.get("TEST_ID", str(uuid.uuid4()))

instrumentation_key = os.environ.get("APPINSIGHTS_INSTRUMENTATIONKEY")
telemetry_client = None
if instrumentation_key:
    telemetry_client = TelemetryClient(instrumentation_key)

print("Test run for '{}' started.".format(test_id))

queries_total = int(os.environ.get("QUERIES_TOTAL", -1))
queries_executed = 0

while queries_executed < queries_total or queries_total < 0:
    raw_query = get_query()
    print("\nTest '{}' executing #{}:\n{}\n".format(test_id, queries_executed, raw_query))

    t = timeit.Timer(functools.partial(cursor.execute, raw_query))
    query_time = t.timeit(number=1)

    print("Query took: {:.2f} seconds".format(query_time))
    queries_executed += 1

    if telemetry_client:
        telemetry_client.track_metric("query_time", query_time, properties={"test_id": test_id})
        telemetry_client.flush()

print("Test run for '{}' ended.".format(test_id))

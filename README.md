# Using Tinybird with an Audit Log

This repository contains the data project —[datasources](./datasources), [pipes](./pipes), and [endpoints](./endpoints)— and [data-generator](./data-generator) scripts for an audit log example of using Tinybird.

Check out this live session demo [video](https://www.youtube.com/watch?v=C9859uVd6uc&list=PLZGPeFpwVFORWK4W-1sMWzYUcS7fOlaQC&index=1) to see how to work with audit logs from Kafka streams in Tinybird.

To clone the repository:

```bash
git clone --branch live-coding-session git@github.com:tinybirdco/demo-audit-log.git

cd demo-audit-log
```

## Working with the Tinybird CLI

To start working with data projects as if they were software projects, let's install the Tinybird CLI in a virtual environment.
Check the [CLI documentation](https://docs.tinybird.co/cli.html) for other installation options and troubleshooting.

```bash
virtualenv -p python3 .e
. .e/bin/activate
pip install tinybird-cli
tb auth --interactive
```

Choose your region: __1__ for _us-east_, __2__ for _eu_

Go to your workspace, copy a token with admin rights and paste it. A new `.tinyb` file will be created.  

## Project description

```bash
├── datasources
│   ├── companies.datasource
│   ├── enriched_events_mv.datasource
│   ├── events_per_min_mv.datasource
│   ├── fixtures
│   │   └── companies.csv
│   └── kafka_audit_log.datasource
├── endpoints
│   ├── api_audit_log.pipe
│   ├── api_count_per_type.pipe
│   ├── api_totals.pipe
│   ├── api_ui_filters.pipe
│   └── events_per_company.pipe
├── pipes
│   ├── mat_enriched_events.pipe
│   └── mat_events_per_min.pipe
```

In the `/datasources` folder we have four Data Sources:

- kafka_audit_log: where we'll be consuming the audit log events from our Kafka topic
- companies: where we will store the information about the companies. The content (a CSV file) is in the fixtures subfolder.
- enriched_events_mv: a materialized view where we store the events adding denormalizing the company info.
- events_per_min: a materialized view where we do an incremental rollup of all the events per type, company, and minute. They are also joined with companies to get the company name.

Five .pipe files in the `/endpoints` folder:

- events_per_company: the first endpoint we created in our live-session.
- api_audit_log: a pipe that retrieves a timestamp and a composed message combining some fields of the events.
- api_totals: just the sum of every event in the kafka_audit_log datasource.
- api_count_per_type: an example of pivoting rows to columns using arrays.
- api_ui_filters: the endpoint used for the fronted to paint the dropdown filters.

Two .pipe files in the `/pipes` folder:
We usually put the .pipe files that trigger a MV into this folder and leave the rest in `/endpoints`

- mat_enriched_events_node: the pipe that materializes in enriched_events_mv.datasource
- mat_events_per_min_node: the pipe that materializes the rollup in events_per_min_mv.datasource

## Ingesting data using kafka

Set your environment variables in a .env file —you can base yours in the _.env_sample_ file.
Then, let's read the environment variables form the .env file

```bash
cat ./.env | while read line; do
    export $line
    # echo $line
done
```

Time to start the generator

```bash
pip install click faker confluent_kafka

python3 data-generator/audit_log_kafka.py --bootstrap-servers $KAFKA_BOOTSTRAP_SERVERS --sasl_plain_username $KAFKA_KEY --sasl_plain_password $KAFKA_SECRET
```

You will be sending events like this one:

```json
{
  "datetime": "2022-05-09T10:09:47.988915",
  "company_id": 3,
  "event": "folder_updated",
  "payload": {
    "entity_id": "4a4979f8b02a481a87c89a5a52ad5390",
    "author": "fwebb@example.com"
  },
  "device": {
    "browser": "Chrome",
    "OS": "iOS"
  }
}
```

Feel free to play with the parameters. You can check them with `python3 data-generator/audit_log_kafka.py --help`

You are welcome to explore and modify the [./data-generator/audit_log_kafka.py](./data-generator/audit_log_kafka.py) script too.

Note: we'll assume you will have your own kafka server with a topic called _audit_log_demo_ that can be consumed with a consumer group id _live-sessions_. If that's not the case, feel free to edit the [./datasources/kafka_audit_log.datasource](./datasources/kafka_audit_log.datasource) file and call the generator with the desired topic: 

`python3 data-generator/audit_log_kafka.py --topic <your_topic>`

## Pushing the data project to your Tinybird workspace

First, create a Kafka connection to let your datasource connect to your Kafka server. You have more details in our [docs](https://docs.tinybird.co/cli/kafka.html).

```bash
tb connection create kafka --bootstrap-servers $KAFKA_BOOTSTRAP_SERVERS --key $KAFKA_KEY --secret $KAFKA_SECRET --connection-name demo_audit_log_connection
```

Then, push the data project —datasources, pipes and fixtures— to your workspace.

```bash
tb push --fixtures
```
  
Your data project is ready for realtime analysis. You can check the UI's Data flow to see how it looks.

![Data flow](data_flow.png?raw=true "Data flow in UI")

## Token security

You now have your Data Sources and pipes that end in API endpoints.

The endpoints need a [token](https://www.tinybird.co/guide/serverless-analytics-api) to be consumed. You should not expose your admin token, so let's create one with more limited scope.

```bash
pip install jq

TOKEN=$(cat .tinyb | jq '.token'| tr -d '"')
HOST=$(cat .tinyb | jq '.host'| tr -d '"')

curl -H "Authorization: Bearer $TOKEN" \
-d "name=endpoints_token" \
-d "scope=PIPES:READ:api_audit_log" \
-d "scope=PIPES:READ:api_totals" \
-d "scope=PIPES:READ:api_ui_filters" \
-d "scope=PIPES:READ:api_count_per_type" \
$HOST/v0/tokens/
```

You will receive a response similar to this:

```json
{
    "token": "<the_newly_ceated_token>",
    "scopes": [
        {
            "type": "PIPES:READ",
            "resource": "api_audit_log",
            "filter": ""
        },
        {
            "type": "PIPES:READ",
            "resource": "api_totals",
            "filter": ""
        },
        {
            "type": "PIPES:READ",
            "resource": "api_ui_filters",
            "filter": ""
        },
        {
            "type": "PIPES:READ",
            "resource": "api_count_per_type",
            "filter": ""
        }
    ],
    "name": "endpoints_token"
}
```

If you want to create a token to share the endpoints that feed the dashboard with, let's say, the company with company_id 1, you can do so with the __row level security__:

```bash
curl -H "Authorization: Bearer $TOKEN" \
-d "name=company_1_token" \
-d "scope=PIPES:READ:api_audit_log" \
-d "scope=PIPES:READ:api_totals" \
-d "scope=PIPES:READ:api_ui_filters" \
-d "scope=PIPES:READ:api_count_per_type" \
-d "scope=DATASOURCES:READ:kafka_audit_log:company_id=1" \
-d "scope=DATASOURCES:READ:companies:company_id=1" \
-d "scope=DATASOURCES:READ:enriched_events_mv:name in (select name from companies where company_id = 1)" \
-d "scope=DATASOURCES:READ:enriched_events_mv:name in (select name from companies where company_id = 1)" \
$HOST/v0/tokens/
```

And now you should see the filters in your response

```json
{
    "token": <the_token>,
    "scopes": [
        {
            "type": "PIPES:READ",
            "resource": "api_audit_log",
            "filter": ""
        },
        {
            "type": "PIPES:READ",
            "resource": "api_totals",
            "filter": ""
        },
        {
            "type": "PIPES:READ",
            "resource": "api_ui_filters",
            "filter": ""
        },
        {
            "type": "PIPES:READ",
            "resource": "api_count_per_type",
            "filter": ""
        },
        {
            "type": "DATASOURCES:READ",
            "resource": "kafka_audit_log",
            "filter": "company_id=1"
        },
        {
            "type": "DATASOURCES:READ",
            "resource": "companies",
            "filter": "company_id=1"
        },
        {
            "type": "DATASOURCES:READ",
            "resource": "enriched_events_mv",
            "filter": "name in (select name from companies where company_id = 1)"
        }
    ],
    "name": "company_1_token"
}
```

This project shows just some of the features of Tinybird. If you have any questions, come along and join our community [Slack](https://join.slack.com/t/tinybird-community/shared_invite/zt-yi4hb0ht-IXn9iVuewXIs3QXVqKS~NQ)!

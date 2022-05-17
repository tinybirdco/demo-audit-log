# Using Tinybird with an Audit Log

This repository contains the data project —[datasources](./datasources), and [endpoints](./endpoints)— and [data-generator](./data-generator) scripts for an audit log example of using Tinybird.

Check out this 5 minute [video](https://youtu.be/NlGtrTGH9dQ) to see how to work with audit logs and Tinybird or this 60 minute [video](https://www.youtube.com/watch?v=C9859uVd6uc) of a live coding session walking you through the whole process.

To clone the repository:

`git clone git@github.com:tinybirdco/demo-audit-log.git`

`cd demo-audit-log`

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
│   ├── audit_log_hfi.datasource
│   ├── companies.datasource
│   └── fixtures
│       └── companies.csv
├── endpoints
│   ├── api_audit_log_enriched.pipe
│   ├── api_audit_log_params.pipe
│   └── api_count_per_type.pipe
```

In the `/datasources` folder we have two Data Sources:
- audit_log_hfi: where we'll be sending audit log events with a python script
- companies: where we will store the information about the companies. The content (a CSV file) is in the fixtures subfolder.

And three .pipe files in the `/endpoints` folder:
- api_audit_log_enriched: a pipe that counts the number of events per company from _audit_log_hfi_ and joins the result with the info in _companies_
- api_audit_log_params: en example with several [dynamic parameters](https://guides.tinybird.co/guide/using-dynamic-parameters-for-changing-aggregation-types-on-the-fly)
- api_count_per_type: an example of pivoting rows to columns using arrays.

Note:
Typically, in big projects, we split the .pipe files across two folders: /pipes and /endpoints
- `/pipes` where we store the pipes ending in a datasource, that is, [materialized views](https://guides.tinybird.co/guide/materialized-views)
- `/endpoints` for the pipes that end in API endpoints. 

## Pushing the data project to your Tinybird workspace

Push the data project —datasources, pipes and fixtures— to your workspace.

```bash
tb push --fixtures
```
  
Your data project is ready for realtime analysis. You can check the UI's Data flow to see how it looks.

![Data flow](data_flow.jpg?raw=true "Data flow in UI")

## Ingesting data using high-frequency ingestion (HFI)

Let's add some data through the [HFI endpoint](https://www.tinybird.co/guide/high-frequency-ingestion).

To do that we have created a python script to generate and send dummy events.

```bash
pip install click faker
python3 data-generator/audit_log_events.py --repeat 100
```

Feel free to play with the parameters. You can check them with `python3 data-generator/audit_log_events.py --help`

## Token security

You now have your Data Sources and pipes that end in API endpoints. 

The endpoints need a [token](https://www.tinybird.co/guide/serverless-analytics-api) to be consumed. You should not expose your admin token, so let's create one with more limited scope.

```bash
pip install jq

TOKEN=$(cat .tinyb | jq '.token'| tr -d '"')
HOST=$(cat .tinyb | jq '.host'| tr -d '"')

curl -H "Authorization: Bearer $TOKEN" \
-d "name=endpoints_token" \
-d "scope=PIPES:READ:api_audit_log_enriched" \
-d "scope=PIPES:READ:api_audit_log_params" \
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
            "resource": "api_audit_log_enriched",
            "filter": ""
        },
        {
            "type": "PIPES:READ",
            "resource": "api_audit_log_params",
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

If you want to create a token to share just `api_audit_log_params` with, let's say, the company with company_id 1, you can do so with the **row level security**:

```bash
curl -H "Authorization: Bearer $TOKEN" \
-d "name=comp_1_token" \
-d "scope=PIPES:READ:api_audit_log_params" \
-d "scope=DATASOURCES:READ:audit_log_hfi:company_id=1" \
$HOST/v0/tokens/
```

This project shows just some of the features of Tinybird. If you have any questions, come along and join our community [Slack](https://join.slack.com/t/tinybird-community/shared_invite/zt-yi4hb0ht-IXn9iVuewXIs3QXVqKS~NQ)!

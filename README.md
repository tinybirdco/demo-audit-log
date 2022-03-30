# Audit log demo

## Intro

This repo contains the data project —[datasources](./datasources), and [endpoints](./endpoints)— and [data-generator](./data-generator) scripts for the audit log demo.

## Working with tinybird CLI

To start working with data projects as if they were software projects, let's install the tinybird CLI in a virtual environment.
Check the [CLI documentation](https://docs.tinybird.co/cli.html) for other installation options and troubleshooting.

```bash
virtualenv -p python3 .e
. .e/bin/activate
pip install tinybird-cli
tb auth --interactive
```

Choose your region: __1__ for _us-east_, __2__ for _eu_

Go to your workspace, copy a token with admin rights and paste it. A new .tinyb file will be created.  

## Pushing the data project to our workspace

Then, push the data project —datasources, pipes and its fixtures— to your workspace.

```bash
tb push --fixtures
```
  
Your data project is ready for realtime analysis. You can check in the UI's data flow how it looks like.

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

In the `/datasources` folder we have two datasources:
- audit_log_hfi: where we'll be sending audit log events with a python script
- companies: where we will store the information about the companies. The content (a CSV file) is in the fixtures subfolder

And three .pipe files in the `/endpoints` folder:
- api_audit_log_enriched: a pipe that counts the number of events per company from _audit_log_hfi_ and joins the result with the info in _companies_
- api_audit_log_params: en example with several [dynamic parameters](https://guides.tinybird.co/guide/using-dynamic-parameters-for-changing-aggregation-types-on-the-fly)
- api_count_per_type: an example of pivoting rows ro columns using arrays

Note: typically, in big projects, we split the .pipe files in two folders: /pipes and /endpoits, with `/pipes` being the one where we store the pipes ending in a datasource, that is, [materialized views](https://guides.tinybird.co/guide/materialized-views), and `/endpoints` for the pipes that end in API endpoints. You'll get there eventutally.

## Ingesting

Let's push some data through our [HFI endpoint](https://www.tinybird.co/guide/high-frequency-ingestion)

For that purpose we have created a python script to generate and send dummy events.

```bash
pip install click faker
python3 data-generator/audit_log_events.py --repeat 1000
```

Feel free to play with the parameters. You can check them with `python3 data-generator/audit_log_events.py --help`

## Token security

You now have your datasources and pipes that end in API endpoints. The endpoints need a [token](https://www.tinybird.co/guide/serverless-analytics-api) to be consumed and it's not a good idea to expose your admin token, so let's create one.

```bash
TOKEN=$(cat .tinyb | jq '.token'| tr -d '"')
HOST=$(cat .tinyb | jq '.host'| tr -d '"')

curl -H "Authorization: Bearer $TOKEN" \
-d "name=endpoints_token" \
-d "scope=PIPES:READ:api_audit_log_enriched" \
-d "scope=PIPES:READ:api_audit_log_params" \
-d "scope=PIPES:READ:api_count_per_type" \
$HOST/v0/tokens/
```

You should receive a response like this one:

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

In case you wanted to create a token to share just `api_audit_log_params` with, let's say, the company with company_id 1, you can do so with the row level security:

```bash
curl -H "Authorization: Bearer $TOKEN" \
-d "name=comp_1_token" \
-d "scope=PIPES:READ:api_audit_log_params" \
-d "scope=DATASOURCES:READ:audit_log_hfi:company_id=1" \
$HOST/v0/tokens/
```

This is just an example of some Tinybird features. If you had any doubt, do not hesitate to contact us in our community slack!

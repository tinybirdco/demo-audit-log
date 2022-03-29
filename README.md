# Audit log demo

## Intro

This repo contains the data project —[datasources](./datasources), [pipes](./pipes), [endpoints](./endpoints)— and [data-generator](./data-generator) scripts of the audit log demo.

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

# oejp-api-example
An Example of Using the Octopus Energy API

## Environment

Add a .env file to your project root like so:
```bash
OCTOPUS_EMAIL=<YOUR EMAIL>
OCTOPUS_PASSWORD=<YOUR PASSWORD>
```

## Run

```bash
uvicorn main:app --reload
```


## Print Usage

Calculate basic statistics about your electricity usage. Saves output as  svg.

```bash
python3 usage.py 2022-09-01 2022-09-30
```
# scr-lifecycle-policy

scr-lifecycle-policy is a tool that does the delete of Docker tags older than n days/hours/minutes on your Scaleway registry container.

```
usage: scr-lifecycle-policy.py [-h] --token TOKEN --image-id IMAGE_ID --grace GRACE [--dry-run DRY_RUN] [--region REGION]

scr-lifecycle-policy is a tool that does the delete of Docker tags older than n days on your Scaleway registry container

options:
  -h, --help           show this help message and exit
  --token TOKEN        Scaleway token
  --image-id IMAGE_ID  The unique ID of the Image
  --grace GRACE        Relative duration in which to ignore references. This value is specified as a time duration value like "30d", "1h", "30m" or "30s". Refs newer than the duration will not be deleted.
  --dry-run DRY_RUN    Dry run mode (yes or no, yes is default value)
  --region REGION      The region you want to target. Possible values are fr-par, nl-ams and pl-waw (fr-par is default value)
```
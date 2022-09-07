#!/usr/bin/env python3
import requests
import logging
import argparse
import json
from datetime import datetime, timedelta

def custom_log_format():
    log_format = (
        '[%(asctime)s] %(levelname)-8s %(message)s')

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler()
        ]
    )

def argumentParser():
    parser = argparse.ArgumentParser(description='scr-lifecycle-policy is a tool that does the delete of Docker tags older than n days on your Scaleway registry container')
    parser.add_argument('--token', help='Scaleway token', required=True)
    parser.add_argument('--image-id', help='The unique ID of the Image', required=True)
    parser.add_argument('--grace', help='Relative duration in which to ignore references. This value is specified as a time duration value like "30d", "1h", "30m" or "30s". Refs newer than the duration will not be deleted.', required=True)
    parser.add_argument('--dry-run', help='Dry run mode (yes or no, yes is default value)', default='yes')
    parser.add_argument('--region', help='The region you want to target. Possible values are fr-par, nl-ams and pl-waw (fr-par is default value)', default='fr-par')
    args = parser.parse_args()
    return args

def get_tags(token, image_id, region):
    headers={'X-Auth-Token': token }
    tags = []
    page = '1'
    new_results = True

    while new_results:
        try:
            url = "https://api.scaleway.com/registry/v1/regions/" + region + "/images/" + image_id + f"/tags?page={page}"
            data = json.loads(requests.get(url,headers=headers,timeout=10).text)
            new_results = data['tags']
            tags.extend(new_results)
            page = int(page) + 1
        except Exception as e:
            logging.exception("The list of tags could not be retrieved from the Scaleway API")
    return tags

def delete_tag(token, tag_id, region):
    url = "https://api.scaleway.com/registry/v1/regions/" + region + "/tags/" + tag_id + "?force=True"
    headers={'X-Auth-Token': token }

    try:
        tag = requests.delete(url,headers=headers,timeout=10)
        return tag.text
    except Exception as e:
        logging.exception("The tag of image could not be deleted from the Scaleway API")

def main():

    custom_log_format()
    args = argumentParser()

    # Check if grace unit is days, minutes ou hours
    grace_unit = args.grace[-1:]
    grace = args.grace.rstrip(grace_unit)
    if grace_unit == 'd':
        grace_unit = 'days'
    elif grace_unit == 'h':
        grace_unit = 'hours'
    elif grace_unit == 'm':
        grace_unit = 'minutes'
    elif grace_unit == 's':
        grace_unit = 'seconds'
    else:
        logging.exception("This unit of time is not supported. This value is specified as a time duration value like 30d, 1h, 30m or 30s.")

    # List of tags present on the registry for the requested image
    tags = get_tags(args.token, args.image_id, args.region)

    # Tag selection to be deleted without change for n days
    tags_to_delete = []
    for tag in tags:
        # Get the last modification date of the tag
        updated_at = tag['updated_at']
        id = tag['id']
        name = tag['name']
        status = tag['status']
        created_at = tag['created_at']
        updated_at = tag['updated_at']

        # Convert the last modification date of the tag to datetime format
        format = "%Y-%m-%dT%H:%M:%S.%fZ"
        updated_at = datetime.strptime(updated_at, format)

        # If the retention period is exceeded
        if (datetime.utcnow() - updated_at) > timedelta(**{grace_unit: int(grace)}):
            # Print and add the tag eligible for deletion to a list
            logging.info(f"Tag {id} with name {name} and {status} status created on {created_at} and updated for last time on {updated_at} is eligible for deletion.")
            tags_to_delete.append(id)

    # List of the tags without any modification since the specified time (dry-run mode)
    logging.info(f"{len(tags_to_delete)} tags are eligible for deletion.\n")
    if args.dry_run == 'yes':
        logging.info("To remove these tags, restart the tool with the --dry-run no option")

    # Deletion of the tags without any modification since the specified time (no dry-run mode)
    if args.dry_run == 'no':
        for tag in tags_to_delete:
            logging.info(f"Preparing to delete the {tag} tag...")
            delete_tag(args.token, tag, args.region)
            logging.info(f"Tag {tag} deleted.\n")
        logging.info(f"{len(tags_to_delete)} tags have been removed !")

if __name__ == '__main__':
    main()
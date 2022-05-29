#!/usr/bin/env python3

import boto3
import click
import logging
from client import *
from botocore.exceptions import ClientError

# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s')


def put_cw_data(boto_client, data):
    logging.debug(f"Pushing metrics to CW: {data}")
    response = boto_client.put_metric_data(
        Namespace='SNMP data',
        MetricData=[
            {
                'MetricName': 'TransmissionBytes',
                'Dimensions':[
                    {
                        'Name': 'hostname',
                        'Value': data['hostname']
                    }
                ],
                'Value': int(data['rx_mbytes']),
                'Unit': 'Bytes'
            }
        ]
    )
    return response

def load_config():
    pass

@click.group()
def query():
    """ Run one snmp polling cycle, then exit"""

@query.command()
def once():
    print("Snmp CloudWatch starting")
    config = Config("sample.config")
    client = Client(config)
    client.once()
    cloudwatch_client = boto3.client('cloudwatch', region_name=config.client['aws_region'])
    print(put_cw_data(cloudwatch_client, client.get_data()))



def main():
    query()

if __name__ == '__main__':
    main()
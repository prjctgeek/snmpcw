#!/usr/bin/env python3
import click
import logging
from client import *

# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')


def put_cw_data(boto_client, data):
    """
    Callback given to the SNMPCW Client
    :param boto_client: boto client object
    :param data:
    :return:
    """
    logging.debug(f"Pushing metrics to CW: {data}")
    response = boto_client.put_metric_data(
        Namespace='SNMP data',
        MetricData=[
            {
                'MetricName': '{}TransmissionBytes'.format(data['interface']),
                'Dimensions':[
                    {
                        'Name': 'hostname',
                        'Value': data['hostname']
                    }
                ],
                'Value': int(data['rx_mbytes']),
                'Unit': 'Bytes'
            },
            {
                'MetricName': '{}RecievedBytes'.format(data['interface']),
                'Dimensions': [
                    {
                        'Name': 'hostname',
                        'Value': data['hostname']
                    }
                ],
                'Value': int(data['tx_mbytes']),
                'Unit': 'Bytes'
            },
        ]
    )
    if '200' not in response:
        logging.warning(response)
    return response


@click.group()
def query():
    """ Run snmp poll, and send to CloudWatch. """


@query.command()
def once():
    """
    Run one snmp poll/CW update and exit.
    :return:
    """
    print("Snmp CloudWatch starting in one-shot mode")
    config = Config("sample.config")
    client = Client(config)
    boto_client = boto3.client('cloudwatch', region_name=config.client['aws_region'])
    print(client.once(put_cw_data, boto_client))


@query.command()
@click.option("-w", "--wait-time", help="Time to wait between polling in seconds. Default 300", default=300)
def poll(wait_time):
    """
    Repeatedly SNMP poll and send data to cloudwatch, sleeping --wait-time seconds.
    :param wait_time:
    :return:
    """
    print(f"Snmp CloudWatch starting in polling mode; sleeping {wait_time}seconds between polls.")
    config = Config("sample.config")
    client = Client(config)
    boto_client = boto3.client('cloudwatch', region_name=config.client['aws_region'])
    try:
        client.poll(put_cw_data, boto_client, wait_time)
    except KeyboardInterrupt:
        print("Exiting polling")


def main():
    query()


if __name__ == '__main__':
    main()
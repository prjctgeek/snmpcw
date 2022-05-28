#!/usr/bin/env python3

import click
import boto3
from client import *

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
    print(client.get_data())


def main():
    query()

if __name__ == '__main__':
    main()
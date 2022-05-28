
import boto3
import ipaddress
import configparser
from pysnmp.hlapi import *


class SnmpCloudWatchErr:
    pass

class Config:
    client = {}

    def __init__(self, file_name):
        self.config = configparser.ConfigParser()
        self.config.read(file_name)
        self.load()

    def load(self):
        self.client['community'] = self.config['general']['community']
        self.client['hostname'] = self.config['client']['hostname']
        self.client['ipaddress'] = self.config['client']['ip']
        self.client['oid_rx'] = self.config['client']['oid_rx']
        self.client['oid_tx'] = self.config['client']['oid_tx']

    def dump(self):
        print(f"community string: {self.config['general']['community']}")
        print(f"client: {self.config['client']['ip']}")


class Result:
    def __init__(self, hostname, tr):
        (error_indication, error_status, error_index, var_binds) = tr
        self._data={"hostname": hostname,
                    "error_indication":error_indication,
                    "error_status":error_status,
                    "error_index":error_index,
                    "var_binds":var_binds}

    def get_value_by_oid(self, oid):
        """
        The snmp library is converting the numerical oid into a partial
        human readible, which screws up the pattern matching.
        pull out a fragment of the oid to match.
        :param oid:
        :return:
        """
        partial = ".".join(oid.split(".")[6:-1])
        for response in self._data['var_binds']:
            if partial in str(response[0]):
                return str(response[1])

    def get_hostname(self):
        return self._data['hostname']


class Client:
    results = {}
    def __init__(self, config:Config):
        self.config = config

    def once(self):
        self.query()

    def query(self):
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.config.client['community'], mpModel=0),
            UdpTransportTarget((self.config.client['ipaddress'], 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.config.client['oid_tx'])),
            ObjectType(ObjectIdentity(self.config.client['oid_rx'])),
        )

        self.results=Result(self.config.client['hostname'],next(iterator))
        #print(self.results.get_value_by_oid(self.config.client['oid_tx']))

    def get_data(self):
        return {"hostname": self.results.get_hostname(),
                "rx_mbytes": self.results.get_value_by_oid(self.config.client['oid_rx']),
                "tx_mbytes": self.results.get_value_by_oid(self.config.client['oid_tx'])}

    # The tx number is sooo munch higher, double check that these are in the right format - they both should be the samew...

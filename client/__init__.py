import boto3
import ipaddress
import configparser
import logging
from time import sleep
from pysnmp.hlapi import *
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class Config:
    client = {}

    def __init__(self, file_name):
        self.config = configparser.ConfigParser()
        self.config.read(file_name)
        self.load()

    def load(self):
        self.client['community'] = self.config['general']['community']
        self.client['hostname'] = self.config['client']['hostname']
        self.client['aws_region'] = self.config['client']['aws_region']
        self.client['interface'] = self.config['client']['interface']
        self.client['ipaddress'] = self.config['client']['ip']
        self.client['oid_rx'] = self.config['client']['oid_rx']
        self.client['oid_tx'] = self.config['client']['oid_tx']

    def dump(self):
        print(f"community string: {self.config['general']['community']}")
        print(f"client: {self.config['client']['ip']}")


class Result:
    """
    Result object from PySNMP
    with the hostname injected in (we could just poll for that too?).
    """

    def __init__(self, hostname, tr):
        (error_indication, error_status, error_index, var_binds) = tr
        if error_indication:
            logging.error(error_status, error_indication)
            raise AttributeError
        self._data = {"hostname": hostname,
                      "error_indication": error_indication,
                      "error_status": error_status,
                      "error_index": error_index,
                      "var_binds": var_binds}

    def get_value_by_oid(self, oid):
        """
        The snmp library is converting the numerical oid into a partial
        human readable, which screws up the pattern matching.
        pull out a fragment of the oid to match.
        Reminder that the var_binds SNMP result can contain many, many results.

        :param oid: numeric string
        :return:
        """
        partial = ".".join(oid.split(".")[6:-1])
        for response in self._data['var_binds']:
            if partial in str(response[0]):
                return str(response[1])

    def get_hostname(self):
        """
        Retrive the hostname we added to the result.
        this could be queries and pulled back out with the get_value_by_oid?
        :return:
        """
        return self._data['hostname']


class Client:
    results = {}

    def __init__(self, config: Config):
        self.config = config

    def once(self, put_data_cb, boto_client):
        """
        Run one SNMP query, use the put_data_cb to give the response back to the caller.
        We don't manage boto in the library; expecting a boto  client object.
        :param put_data_cb:
        :param boto_client:
        :return:
        """
        self.query()
        return put_data_cb(boto_client, self.get_data())

    def poll(self, put_data_cb, boto_client, wait_in_sec):
        """
        Repeatdly call query
        :param put_data_cb:
        :param boto_client:
        :param wait_in_sec:
        :return:
        """
        while True:
            self.query()
            put_data_cb(boto_client, self.get_data())
            sleep(wait_in_sec)

    def query(self):
        """
        Run one SNMP query, store in a Result object
        :return:
        """
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.config.client['community'], mpModel=0),
            UdpTransportTarget((self.config.client['ipaddress'], 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.config.client['oid_tx'])),
            ObjectType(ObjectIdentity(self.config.client['oid_rx'])),
            ObjectType(ObjectIdentity(self.config.client['interface'])),
        )
        self.results = Result(self.config.client['hostname'], next(iterator))

    def get_data(self):
        """
        Combine the SNMP Result object and configuration settings into something we can use.
        :return:
        """
        # TODO: double check that these are really bytes and not MB.  No MIB available from Unifi to convfirm!
        return {"hostname": self.results.get_hostname(),
                "interface": self.results.get_value_by_oid(self.config.client['interface']),
                "rx_mbytes": self.results.get_value_by_oid(self.config.client['oid_rx']),
                "tx_mbytes": self.results.get_value_by_oid(self.config.client['oid_tx'])}

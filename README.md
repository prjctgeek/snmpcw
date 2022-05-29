### snmp cloudwatch

Poll a device with snmp, push the result to AWS Cloudwatch.

Intended as a simple way to monitor a home router. with rx/tx bytes OID, the data could be turned into a BW dashboard.

### Setup

Create a config file at `~/.config/snmpcw/config`, using the sample provided.

Setup a virtual env and run `python3 -m pip install -r requirements.txt`.

### Usage

Credentials setup for aws cli should `just work` with boto. Install aws-cli via pip and running [aws configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) should get you started.


### MIBS

The Unifi MIBS are missing, so in this example, I've reverse engineered the OID by snmpwalking and comparing the UI counters with the snmpwalk output.




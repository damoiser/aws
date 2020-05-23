# auxiliaries functions

import json, sys, subprocess

def print_vaults(account_id):
  aws_vaults_json = json.loads(subprocess.run(['aws', 'glacier', 'list-vaults', '--account-id', account_id], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n'))

  if "VaultList" in aws_vaults_json.keys():
    print("there are " + str(len(aws_vaults_json["VaultList"])) + " available vault(s)")

    for vault in aws_vaults_json["VaultList"]:
      print("* " + vault["VaultName"])

  else:
    print("cannot get all vaults")
    sys.exit()
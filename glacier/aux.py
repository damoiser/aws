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


def get_archive_job_tmp_filename(vault_name, region):
  return "jobs/" + str(region) + "__" + str(vault_name) + "__archive.job"

def get_archive_job_result_filename(vault_name, region):
  return "jobs/" + str(region) + "__" + str(vault_name) + "__archive__results.json"

def get_download_job_filename(vault_name, region, archive_ids):
  return "jobs/" + str(region) + "__" + str(vault_name) + "__" + str(len(archive_ids)) + ".download_job"

def get_download_archive_id(vault_name, archive_id):
  return "downloads/" + str(vault_name) + "/" + archive_id

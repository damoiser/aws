import os, subprocess

def get_aws_config():
  my_env = os.environ.copy()
  my_env["AWS_PAGER"] = ""

  account_id = input("enter account id (blank if same as configured in aws): ")
  if account_id == "":
    # if using the default one use dash
    account_id = "-"

  aws_region = subprocess.run(['aws', 'configure', 'get', 'region'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n')

  region = input("enter region (blank for " + aws_region + "): ")

  if region == "":
    region = aws_region

  return account_id, aws_region, region, my_env
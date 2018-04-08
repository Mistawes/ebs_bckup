# tf\_ebs\_bckup
## a Lambda-powered EBS Snapshot Terraform Module

A Terraform module for creating a Lambda Function that takes automatic snapshots of of all connected EBS volumes of correspondingly tagged instances.
The function is triggered via a CloudWatch event that watches for an instance changing to the `stopped` state. Its purpose is to capture EBS volumes from COB the previous day, for multiple timezones. It works in the basis that we stop instances overnight (outside of production obviously) to reduce costs, but we don't `terminate` them.

## Input Variables:
- `EC2_INSTANCE_TAG` - All instances with this tag name be backed up. Default is `"PreviousEbsBackup"` with a value of `never`. Will be overwritten after 1st EBS snapshot is taken, showing the date of the current backup.
- `RETENTION_DAYS`   - Number of day the created EBS Snapshots will be stored, defaults to `7`
- `unique_name`      - Just a marker for the Terraform stack. Default is "v1"`
- `stack_prefix`     - Prefix for resource generation. Default is `ebs_bckup`
- `regions`          - List of regions in which the Lambda function should run. Requires at least one entry (eg. `["eu-west-1", "us-west-1"]`)

## Outputs
Default outputs are `aws_iam_role_arn` with the value of the created IAM role for the Lambda function and the `lambda_function_name`

## Example usage
In your Terrafom `main.tf` call the module with the required variables.

```
module "ebs_bckup" {
  source = "github.com/mistawes/ebs_bckup"
  EC2_INSTANCE_TAG = "PreviousEbsBackup"
  RETENTION_DAYS   = 7
  unique_name      = "v1"
  stack_prefix     = "ebs_snapshot"
  regions          = ["eu-west-1"]
  instance_state   = "stopped"
  #TAGS_TO_COPY    = ["Name", "CostCentre"]
}
```
## ToDo
Confirm the new tagging method to trigger using Key instead of Value works 100%
Confirm tags are still being included on EBS snapshots.


## Credits
Thanks to [kgorskowski](https://github.com/kgorskowski) for the base ebs_bckup solution.
Thanks to [rastandy](https://github.com/rastandy) for adding more tags to EBS snapshot.
[Mistawes](https://github.com/mistawes) Changed this to allow for multiple timezones, using an instance changing state as a trigger. Also prevents duplicate backups, thanks to the modified tagging method.
# declare necessary variables

variable "EC2_INSTANCE_TAG" {
  default     = "PreviousEbsBackup"
  description = "Tag to identify the EC2 target instances of the Lambda Function"
}
variable "RETENTION_DAYS" {
  default = 7
  description = "Numbers of Days that the EBS Snapshots will be stored (INT)"
}
variable "TAGS_TO_COPY" {
  default = []
  description = "Tags to copy from the EBS Volume to the snapshot"
}
variable "unique_name" {
  default = "v1"
  description = "Enter Unique Name to identify the Terraform Stack (lowercase)"
}

variable "instance_state" {
  default = "stopped"
  description = "Enter the instance state, which will trigger the function to run. E.g. 'stopped', 'running'."
}

variable "stack_prefix" {
  default = "ebs_bckup"
  description = "Stack Prefix for resource generation"
}

variable "regions" {
  type = "list"
  default = "eu-west-1"
}

import boto3
import ConfigParser
import botocore
import datetime
import re
import collections

config = ConfigParser.RawConfigParser()
config.read('./vars.ini')

print('Loading Backup function')

def lambda_handler(event, context):
    regionsStrg = config.get('regions', 'regionList')
    regionsList = regionsStrg.split(',')
    EC2_INSTANCE_TAG = config.get('main', 'EC2_INSTANCE_TAG')
    retention_days = config.getint('main', 'RETENTION_DAYS')
    tags_to_copy_str = config.get('main', 'TAGS_TO_COPY')
    tags_to_copy = set(tags_to_copy_str.split(','))

    for r in regionsList:
        aws_region = r
        print("Checking Region %s" % aws_region)
        account = event['account']
        ec = boto3.client('ec2', region_name=aws_region)
        # Using the instance tag KEY (name) instead of VALUE (like kgorskowski). Saves 'ebs-backup=true' tag.
        reservations = ec.describe_instances(
            Filters=[
                {'Name': [EC2_INSTANCE_TAG], 'Values': 'tag-value'},
            ]
        )['Reservations']
        instances = sum(
            [
                [i for i in r['Instances']]
                for r in reservations
                ], [])

        for instance in instances:
            for dev in instance['BlockDeviceMappings']:
                if dev.get('Ebs', None) is None:
                    # skip non EBS volumes
                    continue
                vol_id = dev['Ebs']['VolumeId']
                instance_id=instance['InstanceId']
                instance_name = ''
                instance_tags = []
                for tags in instance['Tags']:

                    # Create a string with todays date
                    date_stamp = str(datetime.date.today())

                    # Assign instance_name to current instance
                    if tags["Key"] == 'Name':
                        instance_name = tags["Value"]
                        print("Current instance is: " + instance_name)
                    
                    # Add tags to copy to EBS snapshot - ToDo: verify this still works, pasted again below
                    elif tags["Key"] in tags_to_copy:
                            instance_tags += [tags]

                    # Check if there's a backup from today
                    elif tags["Key"] == "PreviousEbsBackup":

                        print("Checking previous backup stamp..")
                        
                        # If there's a tag with a Key of PreviousEbsBackup, with a Value of todays date, skip.
                        if tags["Value"] == date_stamp
                            print("EBS snapshot already exists for " + instance_id + " today.")
                            continue
                        
                        # Otherwise, if the Value is 'never', or from an older date, go ahead and create an EBS snapshot
                        else:
                            # Might need to move this here - if tags["Key"] in tags_to_copy:
                            # Might need to move this here - instance_tags += [tags]
                            print("No previous backup found for " + instance_id + " today.")
                            print("Found EBS Volume %s on Instance %s, creating Snapshot" % (vol_id, instance['InstanceId']))
                            snap = ec.create_snapshot(
                                Description="Snapshot of Instance %s (%s) %s" % (instance_id, instance_name, dev['DeviceName']),
                                VolumeId=vol_id,
                            )
                            snapshot = "%s_%s" % (snap['Description'], str(datetime.date.today()))
                            delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
                            delete_fmt = delete_date.strftime('%Y-%m-%d')
                            ec.create_tags(
                            Resources=[snap['SnapshotId']],
                            Tags = instance_tags + [
                            {'Key': 'DeleteOn', 'Value': delete_fmt},
                            {'Key': 'Name', 'Value': snapshot},
                            {'Key': 'InstanceId', 'Value': instance_id},
                            {'Key': 'InstanceName', 'Value': instance_name},
                            {'Key': 'DeviceName', 'Value': dev['DeviceName']}
                            ]
                            )
                            # Update the PreviousEbsBackup tag with todays date stamp, to prevent more snapshots from today.
                            ec.create_tags(Resources=[instance_id], Tags=[{'Key':'PreviousEbsBackup', 'Value':date_stamp}])
                            print("Backup completed for " + instance_id + ".")

        delete_on = datetime.date.today().strftime('%Y-%m-%d')
        filters = [
            {'Name': 'tag-key', 'Values': ['DeleteOn']},
            {'Name': 'tag-value', 'Values': [delete_on]},
        ]
        snapshot_response = ec.describe_snapshots(OwnerIds=['%s' % account], Filters=filters)
        for snap in snapshot_response['Snapshots']:
            print "Deleting snapshot %s" % snap['SnapshotId']
            ec.delete_snapshot(SnapshotId=snap['SnapshotId'])

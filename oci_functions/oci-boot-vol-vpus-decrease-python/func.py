#
# oci-boot-vol-vpus-decrease-python version 1.0.
#
# Copyright (c) 2020 Navdeep Saini, Inc.
# Licensed under the Apache License v 2.0 as shown at https://www.apache.org/licenses/LICENSE-2.0.txt
# This function will update the VPUs for Boot volume to balanced performamnce i.e. vpus set to 10

import io
import json
import oci

from fdk import response

def decrease_bv_vpus (boot_vol_id):
    signer = oci.auth.signers.get_resource_principals_signer()
    block_storage_client = oci.core.BlockstorageClient(config={}, signer=signer)
    current_vpus = block_storage_client.get_boot_volume(boot_vol_id).data.vpus_per_gb
    if current_vpus == 10:
        return "Boot Vol already at Balanced Performamnce, vpus for boot_vol {0}: {1}".format(boot_vol_id,current_vpus)
    else:
        print("INFO: current vpus for boot_vol {0}: {1}".format(boot_vol_id,current_vpus), flush=True)
    try:
        print('INFO: Updating boot_vol {}'.format(boot_vol_id), flush=True)
        update_boot_volume_details = oci.core.models.UpdateBootVolumeDetails(vpus_per_gb=10)
        resp = block_storage_client.update_boot_volume(boot_volume_id=boot_vol_id, update_boot_volume_details=update_boot_volume_details)
        print(resp, flush=True)
    except Exception as ex:
        print('ERROR: cannot update update_boot_volume {}'.format(boot_vol_id), flush=True)
        raise
    return "The vpus of boot_vol {} is updated to Balanced Performance".format(boot_vol_id)


def handler(ctx, data: io.BytesIO=None):
    try:
        alarm_msg = json.loads(data.getvalue())
        print("INFO: Alarm message: ")
        print(alarm_msg, flush=True)
    except (Exception, ValueError) as ex:
        print(str(ex), flush=True)

    if alarm_msg["type"] == "OK_TO_FIRING":
        if alarm_msg["alarmMetaData"][0]["dimensions"]:
            alarm_metric_dimension = alarm_msg["alarmMetaData"][0]["dimensions"][0]   #assuming the first dimension matches the boot vol to resize
            print("INFO: Boot Vol to resize: ", alarm_metric_dimension["resourceId"], flush=True)
            func_response = decrease_bv_vpus(alarm_metric_dimension["resourceId"])
            print("INFO: ", func_response, flush=True)
        else:
            print('ERROR: There is no metric dimension in this alarm message', flush=True)
            func_response = "There is no metric dimension in this alarm message"
    else:
        print('INFO: Nothing to do, alarm is not FIRING', flush=True)
        func_response = "Nothing to do, alarm is not FIRING"

    return response.Response(
        ctx,
        response_data=func_response,
        headers={"Content-Type": "application/json"}
    )

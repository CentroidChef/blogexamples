# Automatic Storage Performance
Automatically resize VPUs for given block vol based on utilization.

This use case involves writing a function to resize block volume VPUs and creating an alarm that sends a message to that function. When the alarm fires, the Notifications service sends the alarm message to the destination topic, which then fans out to the topic's subscriptions. In this scenario, the topic's subscriptions include the function. The function is invoked on receipt of the alarm message.

![ONS to Functions](https://objectstorage.us-ashburn-1.oraclecloud.com/n/id3nodyt06el/b/public_images/o/Automatic%20vol%20performance.jpg)


## Prerequisites
Before you deploy this sample function, make sure you have run step A, B and C of the [Oracle Functions Quick Start Guide for Cloud Shell](https://www.oracle.com/webfolder/technetwork/tutorials/infographics/oci_functions_cloudshell_quickview/functions_quickview_top/functions_quickview/index.html)
* A - Set up your tenancy
* B - Create application
* C - Set up your Cloud Shell dev environment


## List Applications 
Assuming your have successfully completed the prerequisites, you should see your 
application in the list of applications.
```
fn ls apps
```


## Create or Update your Dynamic Group
In order to use other OCI Services, your function must be part of a dynamic group. For information on how to create a dynamic group, refer to the [documentation](https://docs.cloud.oracle.com/iaas/Content/Identity/Tasks/managingdynamicgroups.htm#To).

When specifying the *Matching Rules*, we suggest matching all functions in a compartment with:
```
ALL {resource.type = 'fnfunc', resource.compartment.id = 'ocid1.compartment.oc1..aaaaaxxxxx'}
```
Please check the [Accessing Other Oracle Cloud Infrastructure Resources from Running Functions](https://docs.cloud.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsaccessingociresources.htm) for other *Matching Rules* options.


## Create or Update IAM Policies
Create a new policy that allows the dynamic group to *use instances*.


Your policy should look something like this:
```
Allow dynamic-group <dynamic-group-name> to manage volume-family in compartment <compartment-name>
```
For more information on how to create policies, check the [documentation](https://docs.cloud.oracle.com/iaas/Content/Identity/Concepts/policysyntax.htm).


## Review and customize your function
Review the following files in the current folder:
* the code of the function, [func.py](./func.py)
* its dependencies, [requirements.txt](./requirements.txt)
* the function metadata, [func.yaml](./func.yaml)

The following piece of code in [func.py](./func.py) should be updated to match your needs. The function here is updating the vpus_per_gb to 10 which corresponds to "Balance performance tier"

## Deploy the function
In Cloud Shell, run the fn deploy command to build the function and its dependencies as a Docker image,
push the image to OCIR, and deploy the function to Oracle Functions in your application.

```
fn -v deploy --app <your app name>
```
e.g.
```
fn -v deploy --app myapp
```


## Configure Oracle Notification Service
This section walks through creating an alarm using the Console and then updating the ONS topic created with the alarm. In this example we are setting alarm for metric "VolumeReadThroughput" and setting threshold at 1gigabytespermin value. If value is equal to or less than 1g, then alarm is triggered. You can choose other metrics and value combinations to fire the alarm. Please plan ahead when setting the alarms, as this step is important to make sure functions are triggered at right time.


On the OCI console, navigate to *Monitoring* > *Alarm Definitions*. Click *Create Alarm*.

On the Create Alarm page, under Define alarm, set up your threshold: 

Metric description: 
* Compartment: (select the compartment that contains your Block Volume)
* Metric Namespace: VolumeReadThroughput
* Metric Name: DiskUtilizationNORMAL
* Interval: 1m
* Statistic: Mean 

Trigger rule:
* Operator: less than or equal to
* Value: 1000000000  
* Trigger Delay Minutes: 1

Select your function under Notifications, Destinations:
* Destination Service: Notifications Service
* Compartment: (select the compartment where you want to create the topic and associated subscriptions)

Topic: Click *Create a topic*
* Topic Name: Alarm Topic
* Subscription Protocol: Function
* Function Compartment: (select the compartment that contains your function)
* Function Application: (select the application that contains your function)
* Function: (select your function)
* Click *Create topic and subscription*

Click Save alarm.


## Test ONS > Fn
First, test the function indivudually.


Update section "resourceId" in [test_alarm.json](./test_alarm.json) with the OCID of the block vol you want to update.

Invoke the function as follows:
```
cat test_alarm.json | fn invoke <your app name> <function name>
```
e.g.:
```
cat test_alarm.json | fn invoke myapp oci-boot-vol-vpus-decrease-python
```

Now, the whole flow can be tested. Connect to an instance in the compartment which has the block volume attached. Stress the disk utilization with the *stress* utility for example.

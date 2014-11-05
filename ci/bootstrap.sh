export AWS_DEFAULT_OUTPUT="text"

AMI="ami-9eaa1cf6"
SSH_USER="ubuntu"

pushd ..
BASEDIR=`pwd`
popd

#aws ec2 describe-images --image-id=${AMI}

function get_keypair () {
  if [[ -z "${KEYPAIR-}" ]]; then
    KEYPAIR=$(aws ec2 describe-key-pairs --query KeyPairs[0].KeyName)
    echo "Defaulting to keypair ${KEYPAIR}"
  fi
}


function get_instancetype () {
  if [[ -z "${INSTANCETYPE-}" ]]; then
    INSTANCETYPE="m3.medium"
    echo "Defaulting to instance type ${INSTANCETYPE}"
  fi
}

function get_instance() {
INSTANCEID=`aws ec2 describe-instances --filters Name=tag:juju-test,Values=1 --query Reservations[].Instances.InstanceId`

 if [[ -z "${INSTANCEID-}" ]]; then
INSTANCEID=`aws ec2 run-instances --image-id=${AMI} --key-name=${KEYPAIR} --instance-type=${INSTANCETYPE} --query Instances[0].InstanceId`
aws ec2 create-tags --resources ${INSTANCEID} --tags Key=juju-test,Value=1
echo "Launching EC2 instance: ${INSTANCEID}"
fi
}

function get_state() {
	local instance_id=$1
aws ec2 describe-instances --instance-id=${instance_id} --query Reservations[].Instances[].State.Name
}

function get_publicip() {
	local instance_id=$1
aws ec2 describe-instances --instance-id=${instance_id} --query Reservations[].Instances[].PublicIpAddress
}

function wait_running() {
  local instance_id=$1
  local i=0
  echo "instance_id=${instance_id}"
  

  while [[ $i -lt 10 ]]; do
    if [[ $i != 0 ]]; then
      sleep 10
    fi
    state=$(get_state ${instance_id})

    if [[ "${state}" == "running" ]]; then
      echo "Instance is running"
      return 0
    fi
    
    echo $i
    let i=i+1
  done

  echo "Timed out waiting for instance to start; state was ${state}"
  return 1
}

get_keypair
get_instancetype


get_instance
wait_running ${INSTANCEID}

IP=$(get_publicip ${INSTANCEID})

ssh ${SSH_USER}@${IP} sudo apt-get install --yes rsync

rsync -avz ${BASEDIR}/ ${SSH_USER}@${IP}:test

ssh ${SSH_USER}@${IP} test/ci/install.sh





export JAVA_HOME=/usr
SCRIPTPATH="`dirname $(readlink -f "$0")`"
export MTURK_CMD_HOME=~/web_scripts/alphabets/results/mturk-results/aws-mturk-clt-1.3.0
HITNAME=classification
TASKNAME="large-data-set_1"
SANDBOX=
for arg in "$@"
do
	if [ "$arg" = "-sandbox" ]; then
		SANDBOX=-sandbox
	fi
done

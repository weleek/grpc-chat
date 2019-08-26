SCRIPT_PATH=$( cd "$(dirname "$0")" ; pwd )
SCRIPT_PARENT_PATH=`echo ${SCRIPT_PATH%/*}`

python -m grpc_tools.protoc -I $SCRIPT_PARENT_PATH/proto network.proto --python_out=$SCRIPT_PATH/proto --grpc_python_out=$SCRIPT_PATH/proto


#!/usr/bin/env bash
# Setting variable
echo "== Set variables =="
declare -a nodes=(172.50.0.2 172.50.0.3 172.50.0.4)
declare -a ports=(5984 5985 5986)
declare -a volumes=("m1" "s1" "s2")
export master_node=172.50.0.2
export master_port=5984
export size=${#nodes[@]}
export user=admin
export pass=admintest

# Installing couchDB cluster
echo "== Create the volumes =="
for (( i=0; i<${size}; i++ )); do
    docker volume create --name=db-data-${volumes[${i}]}
done

echo "== Start the containers =="
docker-compose up -d

sleep 30

echo "== Add nodes to cluster =="
for (( i=0; i<${size}; i++ )); do
  if [ "${nodes[${i}]}" != "${master_node}" ]; then
    curl -X POST -H 'Content-Type: application/json' http://${user}:${pass}@127.0.0.1:${master_port}/_cluster_setup \
      -d "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \"username\": \"${user}\", \"password\":\"${pass}\", \"port\": 5984, \"node_count\": \"${size}\", \
           \"remote_node\": \"${nodes[${i}]}\", \"remote_current_user\": \"${user}\", \"remote_current_password\": \"${pass}\"}"
    curl -X POST -H 'Content-Type: application/json' http://${user}:${pass}@127.0.0.1:${master_port}/_cluster_setup \
      -d "{\"action\": \"add_node\", \"host\":\"${nodes[${i}]}\", \"port\": 5984, \"username\": \"${user}\", \"password\":\"${pass}\"}"
  fi
done

sleep 10

curl http://${user}:${pass}@localhost:${master_port}/_cluster_setup

for port in "${ports[@]}"; do  curl -X GET http://${user}:${pass}@localhost:${port}/_membership; done

# Create database
curl -X PUT -H 'Authorization: Basic YWRtaW46YWRtaW50ZXN0' -H 'Host: localhost:5984' http://localhost:5984/twitter
curl -X PUT -H 'Authorization: Basic YWRtaW46YWRtaW50ZXN0' -H 'Host: localhost:5984' http://localhost:5984/aurin

# Install python dependencies
pip3 install -r requirements.txt

# Start mining twitter data
python3 twitter.py
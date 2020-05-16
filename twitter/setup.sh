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
for ((i = 0; i < ${size}; i++)); do
  docker volume create --name=db-data-${volumes[${i}]}
done

echo "== Start the containers =="
docker-compose up -d

sleep 30

echo "== Setting up master =="
curl -X POST -H "Content-Type: application/json" http://${user}:${pass}@${master_node}:${master_port}/_cluster_setup -d "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \"username\": ${user}, \"password\": ${pass}, \"node_count\":\"3\"}"

echo "== Add nodes to cluster =="
for ((i = 0; i < ${size}; i++)); do
  if [ "${nodes[${i}]}" != "${master_node}" ]; then
    curl -X POST -H 'Content-Type: application/json' http://${user}:${pass}@${master_node}:${master_port}/_cluster_setup \
    -d "{\"action\": \"enable_cluster\", \"bind_address\":\"0.0.0.0\", \"username\": \"${user}\", \"password\":\"${pass}\", \"port\": 5984, \"node_count\": \"${size}\", \
           \"remote_node\": \"${nodes[${i}]}\", \"remote_current_user\": \"${user}\", \"remote_current_password\": \"${pass}\"}"
    curl -X POST -H 'Content-Type: application/json' http://${user}:${pass}@${master_node}:${master_port}/_cluster_setup \
    -d "{\"action\": \"add_node\", \"host\":\"${nodes[${i}]}\", \"port\": \"${ports[${i}]}\", \"username\": \"${user}\", \"password\":\"${pass}\"}"
  fi
done

sleep 10

echo "== Finalizing cluster setup =="
curl -X POST -H "Content-Type: application/json" http://${user}:${pass}@${master_node}:${master_port}/_cluster_setup -d '{"action": "finish_cluster"}'

curl http://${user}:${pass}@${master_node}:${master_port}/_cluster_setup
curl http://${user}:${pass}@${master_node}:${master_port}/_membership


# Create database
curl -X PUT http://${user}:${pass}@${master_node}:${master_port}/twitter

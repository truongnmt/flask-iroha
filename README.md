# MFExpo Server

### Dependencies
- CMake, git, g++, boost, swig, protobuf, python(3), pip(3).

Please refer to [Iroha Installing Dependencies](https://github.com/hyperledger/iroha/blob/master/docs/source/guides/dependencies.rst) to get installation recipes for the tools.

- grpc.io tools `pip install grpcio_tools`
- Iroha Python SDK `pip install iroha`.
- Flask `pip install flask`

### Deploy Iroha server

```
sudo docker stop $(sudo docker ps -aq)
sudo docker rm $(sudo docker ps -aq)
sudo docker volume rm $(sudo docker volume ls)

sudo docker volume create blockstore1
sudo docker volume create blockstore2
sudo docker volume create blockstore3
sudo docker volume create blockstore4

sudo docker network create iroha-network

sudo docker run --name iroha-postgres1 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  --network=iroha-network \
  -d postgres:9.5

sudo docker run --name iroha-postgres2 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5433:5432 \
  --network=iroha-network \
  -d postgres:9.5

sudo docker run --name iroha-postgres3 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5434:5432 \
  --network=iroha-network \
  -d postgres:9.5

sudo docker run --name iroha-postgres4 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5435:5432 \
  --network=iroha-network \
  -d postgres:9.5
```

Then `cd` into `develop` folder.

The following commands should be executed in separate terminal windows because both of them will enter you into container's environment.

```
sudo docker run -it --name iroha1 \
  -p 50051:50051 \
  -p 10001:10001 \
  -v $(pwd):/opt/iroha_data \
  -v blockstore1:/tmp/block_store \
  --network=iroha-network \
  --entrypoint=/bin/bash \
  hyperledger/iroha:develop

sudo docker run -it --name iroha2 \
  -p 50052:50051 \
  -p 10002:10001 \
  -v $(pwd):/opt/iroha_data \
  -v blockstore2:/tmp/block_store \
  --network=iroha-network \
  --entrypoint=/bin/bash \
  hyperledger/iroha:develop

sudo docker run -it --name iroha3 \
  -p 50053:50051 \
  -p 10003:10001 \
  -v $(pwd):/opt/iroha_data \
  -v blockstore3:/tmp/block_store \
  --network=iroha-network \
  --entrypoint=/bin/bash \
  hyperledger/iroha:develop

sudo docker run -it --name iroha4 \
  -p 50054:50051 \
  -p 10004:10001 \
  -v $(pwd):/opt/iroha_data \
  -v blockstore4:/tmp/block_store \
  --network=iroha-network \
  --entrypoint=/bin/bash \
  hyperledger/iroha:develop
```

Now you need to know IP addresses used by Postgeses and Irohas:

```
sudo docker inspect iroha1 | grep -i ipaddr
sudo docker inspect iroha2 | grep -i ipaddr
sudo docker inspect iroha3 | grep -i ipaddr
sudo docker inspect iroha4 | grep -i ipaddr
```

In my case they were:

| | |
| -|- |
| iroha1          | 192.168.80.6 |
| iroha2          | 192.168.80.7 |
| iroha3          | 192.168.80.8 |
| iroha4          | 192.168.80.9 |

We need to create nodes' keypairs, genesis block via composing peers.list and passing it to iroha-cli:
```
$ cat peers.list
192.168.80.6:10001
192.168.80.7:10001
192.168.80.8:10001
192.168.80.9:10001

$ iroha-cli --genesis_block --peers_address peers.list
```

Now we have to compose config files for both Iroha instances:
```
$ cat config1.docker
{
  "block_store_path" : "/tmp/block_store/",
  "torii_port" : 50051,
  "internal_port" : 10001,
  "pg_opt" : "host=iroha-postgres1 port=5432 user=postgres password=mysecretpassword",
  "max_proposal_size" : 10,
  "proposal_delay" : 5000,
  "vote_delay" : 5000,
  "load_delay" : 5000,
  "mst_enable" : false
}

$ cat config2.docker
{
  "block_store_path" : "/tmp/block_store/",
  "torii_port" : 50051,
  "internal_port" : 10001,
  "pg_opt" : "host=iroha-postgres2 port=5432 user=postgres password=mysecretpassword",
  "max_proposal_size" : 10,
  "proposal_delay" : 5000,
  "vote_delay" : 5000,
  "load_delay" : 5000,
  "mst_enable" : false
}

$ cat config3.docker
{
  "block_store_path" : "/tmp/block_store/",
  "torii_port" : 50051,
  "internal_port" : 10001,
  "pg_opt" : "host=iroha-postgres3 port=5432 user=postgres password=mysecretpassword",
  "max_proposal_size" : 10,
  "proposal_delay" : 5000,
  "vote_delay" : 5000,
  "load_delay" : 5000,
  "mst_enable" : false
}

$ cat config4.docker
{
  "block_store_path" : "/tmp/block_store/",
  "torii_port" : 50051,
  "internal_port" : 10001,
  "pg_opt" : "host=iroha-postgres4 port=5432 user=postgres password=mysecretpassword",
  "max_proposal_size" : 10,
  "proposal_delay" : 5000,
  "vote_delay" : 5000,
  "load_delay" : 5000,
  "mst_enable" : false
}

# in first docker container being in the folder where iroha-cli(peers.list) was executed
irohad --config config1.docker --genesis_block genesis.block --keypair_name node0

# the same precondition for the second and third container
irohad --config config2.docker --genesis_block genesis.block --keypair_name node1
irohad --config config3.docker --genesis_block genesis.block --keypair_name node2
irohad --config config4.docker --genesis_block genesis.block --keypair_name node3
```

Now open one more terminal window on a host system and enter one of already running containers:
```
sudo docker exec -it iroha1 /bin/bash

# now you are inside the container with the first iroha
iroha-cli --account_name admin@test

sudo docker exec -it iroha-postgres1 psql -U postgres
```

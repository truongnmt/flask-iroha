import sys
import iroha

import iroha_schema.transaction_pb2 as transaction_pb2
import iroha_schema.endpoint_pb2 as endpoint_pb2
import iroha_schema.endpoint_pb2_grpc as endpoint_pb2_grpc
import iroha_schema.queries_pb2 as queries_pb2
import grpc
import time
from random import randint

# config
tx_builder = iroha.ModelTransactionBuilder()
query_builder = iroha.ModelQueryBuilder()
crypto = iroha.ModelCrypto()

creator = "admin@test"
IP = "localhost"
PORT = "50051"
DOMAIN = "test"
ASSET = "test"
query_counter = 1
admin_priv = open("admin@test.priv", "r").read()
admin_pub = open("admin@test.pub", "r").read()
key_pair = crypto.convertFromExisting(admin_pub, admin_priv)

def current_time():
    return int(round(time.time() * 1000))

# Return True if transaction is COMMITTED
def get_status(tx, port):
    tx_hash = tx.hash().blob()
    tx_hash = bytes(tx_hash)
    request = endpoint_pb2.TxStatusRequest()
    request.tx_hash = tx_hash

    channel = grpc.insecure_channel(IP + ":" + port)
    stub = endpoint_pb2_grpc.CommandServiceStub(channel)

    response = stub.Status(request)
    status = endpoint_pb2.TxStatus.Name(response.tx_status)
    print("Status: " + status)
    if status != "COMMITTED":
        return False
    return True

def print_status_streaming(tx, port):
    print("Hash of the transaction: ", tx.hash().hex())
    tx_hash = tx.hash().blob()
    tx_hash = bytes(tx_hash)
    # Create request
    request = endpoint_pb2.TxStatusRequest()
    request.tx_hash = tx_hash
    # Create connection to Iroha
    channel = grpc.insecure_channel(IP + ":" + port)
    stub = endpoint_pb2_grpc.CommandServiceStub(channel)
    # Send request
    response = stub.StatusStream(request)

    for status in response:
        print("Status of transaction:")
        print(status)

def send_tx(tx, key_pair, port):
    print("Send tx")
    print(port)
    tx_blob = iroha.ModelProtoTransaction(tx).signAndAddSignature(key_pair).finish().blob()
    proto_tx = transaction_pb2.Transaction()

    proto_tx.ParseFromString(bytes(tx_blob))
    channel = grpc.insecure_channel(IP + ":" + port)
    stub = endpoint_pb2_grpc.CommandServiceStub(channel)

    stub.Torii(proto_tx)

def send_query(query, key_pair, port):
    query_blob = iroha.ModelProtoQuery(query).signAndAddSignature(key_pair).finish().blob()

    proto_query = queries_pb2.Query()
    proto_query.ParseFromString(bytes(query_blob))
    channel = grpc.insecure_channel(IP + ":" + port)
    query_stub = endpoint_pb2_grpc.QueryServiceStub(channel)
    query_response = query_stub.Find(proto_query)

    return query_response

def get_account(account):
    global query_counter
    query_counter += 1
    account_id = account + "@" + DOMAIN
    query = query_builder.creatorAccountId(creator) \
        .createdTime(current_time()) \
        .queryCounter(query_counter) \
        .getAccount(account_id) \
        .build()

    port = random_port()

    query_response = send_query(query, key_pair, port)
    return query_response

def transfer_coin(sender, recipient, message, amount):
    asset_id = ASSET + "#" + DOMAIN
    sender = sender + "@" + DOMAIN
    recipient = recipient + "@" + DOMAIN
    tx = tx_builder.creatorAccountId(creator) \
        .createdTime(current_time()) \
        .transferAsset(sender, recipient, asset_id, message, str(amount)).build()

    port = random_port()

    send_tx(tx, key_pair, port)
    print_status_streaming(tx, port)
    return get_status(tx, port)

def grant_can_transfer_my_assets_permission_to_admin(account_id, key_pair):
    tx = tx_builder.creatorAccountId(account_id) \
        .createdTime(current_time()) \
        .grantPermission(creator, iroha.Grantable_kTransferMyAssets) \
        .build()

    port = random_port()

    send_tx(tx, key_pair, port)
    print_status_streaming(tx, port)
    return get_status(tx, port)

def grant_can_transfer_my_assets_permission_to_admin(account_id, key_pair):
    tx = tx_builder.creatorAccountId(account_id) \
        .createdTime(current_time()) \
        .grantPermission(creator, iroha.Grantable_kTransferMyAssets) \
        .build()

    port = random_port()

    send_tx(tx, key_pair, port)
    print_status_streaming(tx, port)
    return get_status(tx, port)

def create_account_with_100_coin(account_name, user_kp):
    asset_id = ASSET + "#" + DOMAIN
    account_id = account_name + "@" + DOMAIN
    tx = tx_builder.creatorAccountId(creator) \
        .createdTime(current_time()) \
        .createAccount(account_name, DOMAIN, user_kp.publicKey()) \
        .transferAsset("admin@test", account_id, asset_id, "", str(100)) \
        .build()

    port = random_port()

    send_tx(tx, key_pair, port)
    print_status_streaming(tx, port)
    return get_status(tx, port)

def get_account(account):
    global query_counter
    query_counter += 1
    account_id = account + "@" + DOMAIN
    query = query_builder.creatorAccountId(creator) \
        .createdTime(current_time()) \
        .queryCounter(query_counter) \
        .getAccount(account_id) \
        .build()

    port = random_port()

    query_response = send_query(query, key_pair, port)
    return query_response

def get_account_asset(account):
    global query_counter
    query_counter += 1
    account_id = account + "@" + DOMAIN
    query = query_builder.creatorAccountId(creator) \
        .createdTime(current_time()) \
        .queryCounter(query_counter) \
        .getAccountAssets(account_id) \
        .build()

    port = random_port()

    query_response = send_query(query, key_pair, port)
    return query_response

def random_port():
    i = randint(1, 3)
    port = "5005" + str(i)
    print("PORT is: " + str(port))
    return str(port)

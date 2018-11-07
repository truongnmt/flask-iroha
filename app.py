import iroha

from flask import Flask, request, jsonify
import iroha_schema.iroha_helper as IrohaHelper
from google.protobuf.json_format import MessageToDict

app = Flask(__name__)

@app.route("/api/create_account", methods=["GET"])
def create_account():
    account_name = request.args.get("account_name")
    if is_string_nil_or_empty(account_name):
        return json_response(False, "Please send your account name", {}, 404)
    else:
        response = MessageToDict(IrohaHelper.get_account(account_name))
        # in case we don't have account_name on network
        if "errorResponse" in response and response["errorResponse"]["reason"] == "NO_ACCOUNT":
            user_kp = iroha.ModelCrypto().generateKeypair()
            is_success = IrohaHelper.create_account_with_100_coin(account_name, user_kp)
            if is_success:
                account_id = account_name + "@moneyforward"
                IrohaHelper.grant_can_transfer_my_assets_permission_to_admin(account_id, user_kp)
                return json_response(is_success, "Created Account Successfully", \
                    {"public_key": user_kp.publicKey().hex(), "balance": 100}, 200)
            else:
                return json_response(is_success, "Can't create account", {}, 501)
        else:
            response = IrohaHelper.get_account_asset(account_name)
            assets_response = MessageToDict(response)["accountAssetsResponse"]
            balance = assets_response["accountAssets"][-1]["balance"]
            return json_response(True, "", {"balance": balance}, 200)

def json_response(is_success, message, data, status_code):
    result = {
        "is_success": is_success,
        "message": message,
        "data": data
    }
    resp = jsonify(result)
    resp.status_code = status_code
    return resp

def is_string_nil_or_empty(string):
    if string is None or len(string) == 0:
        return True
    return False

if __name__ == "__main__":
    app.run(host="0.0.0.0")

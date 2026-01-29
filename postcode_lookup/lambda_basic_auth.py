import ipaddress
import os

DC_AUTH = "Basic ZGM6ZGM="  # dc:dc
ALLOWLIST = os.environ.get("IP_ALLOWLIST", "")


def lambda_handler(event, context):
    headers = event.get("headers") or {}

    xff = headers.get("X-Forwarded-For", "")
    client_ip = xff.split(",")[0].strip() if xff else ""

    if client_ip and _ip_in_allowlist(client_ip):
        return _allow("ip-allowlisted")

    auth = headers.get("Authorization") or headers.get("authorization")
    if auth == DC_AUTH:
        return _allow("basic-auth")

    return {
        "principalId": "anonymous",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": "*",
                }
            ],
        },
    }


def _ip_in_allowlist(client_ip: str) -> bool:
    try:
        ip = ipaddress.ip_address(client_ip)
    except ValueError:
        return False

    for item in [x.strip() for x in ALLOWLIST.split(",") if x.strip()]:
        try:
            net = (
                ipaddress.ip_network(item, strict=False)
                if "/" in item
                else ipaddress.ip_network(item + "/32")
            )
            if ip in net:
                return True
        except ValueError:
            pass

    return False


def _allow(principal_id: str):
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "*",
                }
            ],
        },
    }

import requests
import json
import os

infoblox = os.environ.get("INFOBLOX_GRIDMASTER", default='10.0.0.241')
username = os.environ.get("INFOBLOX_USERNAME", default='admin'),
password = os.environ.get("INFOBLOX_PASSWORD", default='infoblox')


def err_res(message):
    return {'status': False, 'message': message}


def create_next_avail_network_container(parent_network: str, new_network_size: int, new_network_name):
    url = f"https://{infoblox}/wapi/v2.11.2/request"
    payload = [
        {
            "method": "GET",
            "object": "networkcontainer",
            "data": {
                # "*SifLoc:": "Texas",
                "network": parent_network,
                "network_view": "default"
            },
            "assign_state": {
                "netw_ref": "_ref"
            },
            "discard": True
        },
        {
            "method": "POST",
            "object": "networkcontainer",
            "data": {
                "network": {
                    "_object_function": "next_available_network",
                    "_result_field": "networks",
                    "_parameters": {
                        "cidr": new_network_size
                    },
                    "_object_ref": "##STATE:netw_ref:##"
                },
                "network_view": "default",
                "comment": new_network_name,
                # "extattrs": {
                #     "Test1": {
                #         "value": "dg11"
                #     },
                #     "Test2": {
                #         "value": "vince"
                #     }
                # }
            },
            "enable_substitution": True
        }
    ]
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False, auth=("admin", "infoblox"))
    except requests.exceptions.HTTPError as http_err:
        message = f'HTTP error occurred connecting to Infoblox: {http_err}'
        print(message)
        return err_res(message)
    except requests.exceptions.ConnectionError as conn_err:
        message = f'Error connecting to Infoblox: {conn_err}'
        print(message)
        return err_res(message)
    except requests.exceptions.Timeout as timeout_err:
        message = f'Timeout to Infoblox error: {timeout_err}'
        print(message)
        return err_res(message)
    except Exception as err:
        message = f'An error occurred sending request to infoblox: {err}'
        print(message)
        return err_res(message)
    print(response.text)
    # print(response.status_code)
    # print(response)

    if response.status_code == 201:
        # Network Container was created
        network = json.loads(response.text)[0].split('/')

        message = f"Network {network[1].split(':')[1]}/{network[2]}  was assigned"
        return {'status': True, 'message': message}
    elif response.status_code == 401:
        # Credentials for infoblox grid master is incorrect
        message = f"Unable to authenticate to Infoblox grid master ({infoblox})"
        return err_res(message)
    elif response.status_code == 400:
        message = json.loads(response.text)['Error']
        print(message)
        return err_res(message)
    else:
        message = response.text
        return err_res(message)


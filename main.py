import requests
import os
import json
import time

API_AUTH = {"X-API-Client-ID": os.environ['HIP_ID'], "X-API-Token": os.environ["HIP_KEY"]}
CAPTURE_TIME = int(os.environ.get('CAPTURE_TIME', 1))
HIP_URL = os.environ['HIP_URL']

if __name__ == "__main__":
    r = requests.get(f"{HIP_URL}/api/v1/hipservices", headers=API_AUTH, verify=False)
    hip_ids = [{"id": item["id"], "name": item["title"]} for item in r.json() if item["active"]]
    # print(json.dumps(r.json(), indent=2))
    HS_COUNT = len(hip_ids) + 1
    # print(hip_ids)
    hip_ports = {}
    for hs in hip_ids:
        r = requests.get(f"{HIP_URL}/api/v1/hipservices/{hs['id']}/ports", headers=API_AUTH, verify=False)
        # print(json.dumps(r.json(), indent=2))
        for port in r.json():
            if port["port_type"] == 'shared':
                hip_ports[hs['id']] = {"if": port["interface"], "name": hs['name']}
    for hip_id, port in hip_ports.items():
        r = requests.post(f"{HIP_URL}/api/v1/hipservices/{hip_id}/pcap", headers=API_AUTH, verify=False, json={"capture_interface": port["if"], "max_time": CAPTURE_TIME})
    time.sleep(CAPTURE_TIME * 60)
    for hip_id, values in hip_ports.items():
        r = requests.get(f"{HIP_URL}/api/v1/hipservices/{hip_id}/pcap", headers=API_AUTH, verify=False)
        with open(f"pcaps/{values['name'].replace(' ','_')}.pcap", "wb+") as f:
            f.write(r.content)
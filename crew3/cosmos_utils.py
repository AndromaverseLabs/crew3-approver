import requests


def get_chain_from_addr(addr):
    if addr[:6] == "cosmos":
        return "cosmos"
    if addr[:5] == "stars":
        return "stars"
    if addr[:4] == "osmo":
        return "osmo"
    return None


def fetch_delegation(api_url, delegator_addr, validator_addr, digits=6):
    url = f"{api_url}" f"/validators/{validator_addr}" f"/delegations/{delegator_addr}"
    data = requests.get(url).json()
    udenom = int(data["delegation_response"]["balance"]["amount"])
    return udenom / pow(10, digits)


def fetch_cosmos_delegation(delegator_addr, validator_addr):
    api_url = "https://lcd-cosmoshub.blockapsis.com/cosmos/staking/v1beta1"
    return fetch_delegation(api_url, delegator_addr, validator_addr, 6)


def fetch_stargaze_delegation(delegator_addr, validator_addr):
    api_url = "https://stargaze-api.polkachu.com/cosmos/staking/v1beta1"
    return fetch_delegation(api_url, delegator_addr, validator_addr, 6)


def fetch_osmo_delegation(delegator_addr, validator_addr):
    api_url = "https://osmosis-api.polkachu.com/cosmos/staking/v1beta1"
    return fetch_delegation(api_url, delegator_addr, validator_addr, 6)

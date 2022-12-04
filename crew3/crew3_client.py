import logging

import requests

from . import cosmos_utils

LOG = logging.getLogger(__name__)

validators = {
    "cosmos": "cosmosvaloper1l034wm5h2hktkdq75fd6p099kwzhljn7q7sqnr",
    "stars": "starsvaloper1jtjld0gnn4np74m6c6qn8xcazzvc2j9mnp0wxg",
    "osmo": "osmovaloper1l034wm5h2hktkdq75fd6p099kwzhljn7hxlx79",
}

get_delegation = {
    "cosmos": cosmos_utils.fetch_cosmos_delegation,
    "stars": cosmos_utils.fetch_stargaze_delegation,
    "osmo": cosmos_utils.fetch_osmo_delegation,
}

quest_info = {
    "bbb788ea-29eb-45ac-9574-2203ae7ef093": {"chain": "osmo", "amount": 50},
    "13b8bef3-88b5-4f7d-86ae-761f83c34d9b": {"chain": "osmo", "amount": 500},
    "b46dbee0-e1bc-4eef-bd85-01176ff8eafe": {"chain": "cosmos", "amount": 5},
    "195f8227-8f42-44e5-859f-7272ae4eb69e": {"chain": "cosmos", "amount": 50},
    "ddc24553-339f-4ee5-9918-afc0365b8054": {"chain": "cosmos", "amount": 500},
    "386acb23-203b-494d-99e4-3126ebc77ad9": {"chain": "stars", "amount": 1000},
}


class Crew3Client:
    def __init__(self, api_key: str, subdomain: str):
        self.api_key = api_key
        self.subdomain = subdomain
        self.root_url = f"https://api.crew3.xyz/communities/{subdomain}"

    def _create_headers(self):
        return {"x-api-key": self.api_key}

    def _post(self, path: str, content: dict):
        headers = self._create_headers()
        url = f"{self.root_url}/{path}"
        return requests.post(url, json=content, headers=headers)

    def _get(self, path: str):
        headers = self._create_headers()
        url = f"{self.root_url}/{path}"
        return requests.get(url, headers=headers)

    def review_quest(self, status: str, quest_id: str, comment: str = ""):
        content = {"claimedQuestIds": [quest_id], "status": status, "comment": comment}
        return self._post("claimed-quests/review", content)

    def fetch_pending_quests(self):
        quests = self._get("claimed-quests").json()["data"]
        return filter(lambda x: x["status"] == "pending", quests)

    def review_delegation_quest(self, quest):
        quest_id = quest["questId"]
        claim_id = quest["id"]
        if quest_id not in quest_info:
            LOG.warning(f"Quest id {quest_id} not found")
            return

        info = quest_info[quest_id]
        chain = info["chain"]
        expected_amount = info["amount"]
        addr = quest["submission"]["value"]
        LOG.info(f"\n\nQuest {claim_id} expecting {expected_amount} {chain}")

        try:
            amount_delegated = get_delegation[chain](addr, validators[chain])
            LOG.info(f"{addr} delegated {amount_delegated} {chain}")
        except:
            LOG.warning(f"Unable to fetch {chain} delegation from {addr}")
            if addr[:3] != chain[:3]:
                self.review_quest(
                    "fail",
                    claim_id,
                    f"Not sure this is a valid {chain} address. Please re-submit.",
                )
            return

        if amount_delegated >= expected_amount:
            comment = "Thank you for your delegation!"
            LOG.info(f"✅ Accepting review: {comment}")
            response = self.review_quest("success", claim_id, comment)
        else:
            comment = f"I'm only seeing a delegation of {amount_delegated} ${chain.upper()} and expected {expected_amount}"
            LOG.warning(f"🚫 Rejecting review: {comment}")
            response = self.review_quest("fail", claim_id, comment)

        LOG.info(f"Status: {response.status_code} Content: {response.json()}")

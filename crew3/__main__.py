import logging
import os

from .crew3_client import Crew3Client

logging.basicConfig(level="INFO")

LOG = logging.getLogger(__name__)
api_key = os.environ.get("CREW3_API_KEY")
crew3_client = Crew3Client(api_key, "andromaverse")


quests = crew3_client.fetch_pending_quests()
for quest in quests:
    crew3_client.review_delegation_quest(quest)

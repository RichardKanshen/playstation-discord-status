import logging
import sys
import time

import yaml
from psnawp_api import psnawp

from const import *
from integration import Integration


class PlaystationDiscordStatus:

    def __init__(self):

        # Init logging
        self.log = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(LOGGING_FORMAT, datefmt=LOGGING_DATE_FORMAT)
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.INFO)

        # Load config
        with open("config.yml") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

        # Config variables
        self.NPSSO_KEY = self.config["NPSSO_KEY"]
        self.PLAYSTATION_ONLINE_ID = self.config["PLAYSTATION_ONLINE_ID"]
        self.CLIENT_APP_ID = self.config["CLIENT_APP_ID"]

        # System (PS4, PS5)
        self.system = None

        # Integration helper
        self.integration = Integration(self)

    def run(self):

        psnawp_client = psnawp.PSNAWP(self.NPSSO_KEY)

        previous_presence = None
        previous_status = None

        while True:

            user_online_id = psnawp_client.user(online_id=self.PLAYSTATION_ONLINE_ID)
            presence = user_online_id.get_presence()

            if presence != previous_presence:
                
                print(presence)

                online_status = presence["basicPresence"]["primaryPlatformInfo"]["onlineStatus"]

                if online_status == "offline" and online_status != previous_status:

                    # Remove the presence
                    self.integration.clear_presence()

                else:

                    # Display correct system in presence
                    platform = presence["basicPresence"]["primaryPlatformInfo"]["platform"]
                    if platform == "ps5":
                        self.system = "ps5"
                    elif platform == "ps4":
                        self.system = "ps4"
                    self.integration.connect_presence(self.CLIENT_APP_ID)

                    if "gameTitleInfoList" not in presence["basicPresence"]:
                        # User isn't playing a game
                        self.integration.online_not_ingame()

                    else:

                        game_info = presence["basicPresence"]["gameTitleInfoList"][0]
                        self.integration.online_ingame(game_info)

                previous_status = online_status

            previous_presence = presence
            time.sleep(15)


if __name__ == "__main__":
    psd_status = PlaystationDiscordStatus()
    psd_status.run()

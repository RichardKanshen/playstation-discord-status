import time

from pypresence import Presence

supported_games = [
    "CUSA11106_00", # Taiko no Tatsujin: Drum Session!
    "CUSA06211_00", # Hatsune Miku: Project DIVA Future Tone
    "CUSA28000_00", # DDLC+
    "CUSA02168_00", # Gran Turismo Sport
    "CUSA00744_00", # Minecraft
    "CUSA00265_00", # Minecraft PlayStation®4 Edition (Legacy)
    "CUSA03397_00", # LEGO® STAR WARS™: The Force Awakens
    "CUSA01073_00", # Ratchet & Clank
    "CUSA20108_00", # Super Animal Royale
    "CUSA00572_00", # SHAREfactory™
    "CUSA06122_00", # Roblox
    "CUSA01433_00", # Rocket League®
]

system_names = {
    "ps4": "PlayStation®4",
    "ps5": "PlayStation®5",
}


class Integration:

    def __init__(self, controller):

        # Controller to access vars
        self.controller = controller

        # RPC client
        self.rpc = None

        # Current activity
        self.current_activity = None

        # Start time of activity
        self.start_time = None

    def clear_presence(self):
        if self.rpc:
            self.rpc.clear()
        self.current_activity = None
        self.start_time = None
        self.controller.log.info("User is now offline.")

    def connect_presence(self, app_id):
        if self.rpc:
            self.rpc.clear()
        self.rpc = Presence(app_id, pipe=0)
        self.rpc.connect()

    def online_not_ingame(self):

        if "online" != self.current_activity:
            start_time = int(time.time())
        else:
            start_time = self.start_time

        opts = {
            "details": "Online",
            "state": "Not in-game",
            "start": start_time,
            "small_image": self.controller.system,
            "small_text": system_names[self.controller.system],
        }
        self.rpc.update(**opts)
        self.current_activity = "online"
        self.start_time = start_time
        self.controller.log.info("User is online but not in-game.")

    def online_ingame(self, game_info):

        #print(game_info)

        game_id = game_info["npTitleId"]
        game_title = game_info.get("titleName")
        if game_info.get("gameStatus"):
            game_details = game_info['gameStatus']
        else:
            game_details = None

        if game_id != self.current_activity:
            start_time = int(time.time())
        else:
            start_time = self.start_time

        if game_id in supported_games:
            large_image = game_id.lower()
        else:
            large_image = self.controller.system
            if "npTitleIconUrl" in game_info:
                self.controller.log.debug(f"Unsupported game, game icon can be added from: {game_info['npTitleIconUrl']}")
            else:
                self.controller.log.debug(f"Unsupported game, game icon url could not be found. try searching on Mobygames :3")
        
        opts = {
                "details": game_title,
                "start": start_time,
                "small_image": self.controller.system,
                "small_text": system_names[self.controller.system],
                "large_text": game_title
            }
        
        if large_image != self.controller.system:
            opts["large_image"] = large_image
        
        if game_details:
            opts["state"] = game_details
        
        print(opts)
        self.rpc.update(**opts)
        self.current_activity = game_id
        self.start_time = start_time
        self.controller.log.info(f"User is playing {game_title} on the {system_names[self.controller.system]}.")

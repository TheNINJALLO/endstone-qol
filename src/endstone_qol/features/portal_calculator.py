import math
from endstone import Player

class PortalCalculatorFeature:
    def __init__(self, plugin):
        self.plugin = plugin

    def handle_command(self, player: Player):
        loc = player.location
        try:
            dim_name = str(loc.dimension.name).lower()
        except Exception:
            dim_name = "overworld"
            
        if dim_name == "the_end":
            player.send_error_message("Nether portals cannot be built in the End.")
            return
            
        if dim_name == "overworld":
            target_x = math.floor(loc.x / 8)
            target_z = math.floor(loc.z / 8)
            target_dim = "Nether"
        elif dim_name == "nether":
            target_x = math.floor(loc.x * 8)
            target_z = math.floor(loc.z * 8)
            target_dim = "Overworld"
        else:
            player.send_error_message("You must be in the Overworld or Nether to use this command.")
            return
            
        player.send_message(f"§e--- Corresponding Portal Location in {target_dim} ---")
        player.send_message(f"§bX: §f{target_x}")
        player.send_message(f"§bY: §f{math.floor(loc.y)} §7(Approximate matching height)")
        player.send_message(f"§bZ: §f{target_z}")

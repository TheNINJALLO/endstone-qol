import math

class WailaHudFeature:
    def __init__(self, plugin):
        self.plugin = plugin

    def run_loop(self):
        for player_name in list(self.plugin.waila_enabled_players):
            player = self.plugin.server.get_player(player_name)
            if not player:
                self.plugin.waila_enabled_players.discard(player_name)
                continue
                
            try:
                loc = player.location
                dir_vec = loc.direction
                
                target_block = None
                for step in range(1, 150):
                    distance = step * 0.1
                    x = loc.x + dir_vec.x * distance
                    # Eye height is roughly 1.62 in Bedrock
                    y = loc.y + 1.62 + dir_vec.y * distance
                    z = loc.z + dir_vec.z * distance
                    
                    try:
                        bx = math.floor(x)
                        by = math.floor(y)
                        bz = math.floor(z)
                        b = player.dimension.get_block_at(bx, by, bz)
                        if b and "air" not in str(b.type).lower():
                            target_block = b
                            break
                    except Exception:
                        break
                        
                if target_block:
                    name = str(target_block.type).replace("minecraft:", "").replace("_", " ").title()
                    
                    states = getattr(target_block, 'states', {})
                    meta_str = ""
                    if "growth" in states:
                        meta_str += f" | Growth: {states['growth']}"
                    if "age" in states:
                        meta_str += f" | Age: {states['age']}"
                    if "fill_level" in states:
                        meta_str += f" | Fill: {states['fill_level']}"
                        
                    player.send_tip(f"§aWAILA: §f{name}§e{meta_str}")
            except Exception as e:
                self.plugin.logger.warning(f"WAILA loop error for {player_name}: {e}")

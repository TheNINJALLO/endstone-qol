import math

class EntityRadarFeature:
    def __init__(self, plugin):
        self.plugin = plugin

    def run_loop(self):
        hostile_mobs = ["zombie", "skeleton", "creeper", "spider", "enderman", "witch", "slime", "phantom", "pillager", "ravager"]
        
        for player_name in list(self.plugin.radar_enabled_players):
            player = self.plugin.server.get_player(player_name)
            if not player:
                self.plugin.radar_enabled_players.discard(player_name)
                continue
                
            try:
                for actor in player.dimension.actors:
                    if actor == player or actor.is_dead:
                        continue
                        
                    dx = actor.location.x - player.location.x
                    dy = actor.location.y - player.location.y
                    dz = actor.location.z - player.location.z
                    dist_sq = dx*dx + dy*dy + dz*dz
                    
                    if dist_sq <= 400: 
                        type_str = str(actor.type).lower()
                        if any(mob in type_str for mob in hostile_mobs):
                            dist = math.sqrt(dist_sq)
                            if dist > 0:
                                nx = dx / dist
                                ny = dy / dist
                                nz = dz / dist
                            else:
                                nx, ny, nz = 0, 0, 0
                                
                            px = player.location.x + (nx * 2)
                            py = player.location.y + 1.5 + (ny * 2)
                            pz = player.location.z + (nz * 2)
                            
                            player.spawn_particle("minecraft:basic_flame_particle", px, py, pz)
            except Exception as e:
                self.plugin.logger.warning(f"Radar loop error for {player_name}: {e}")

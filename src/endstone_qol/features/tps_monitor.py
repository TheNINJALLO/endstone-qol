from endstone import ColorFormat

class TpsMonitorFeature:
    def __init__(self, plugin):
        self.plugin = plugin

    def run_loop(self):
        tps = getattr(self.plugin.server, 'tps', 20.0)
        
        if tps >= 18.0:
            color = ColorFormat.GREEN
        elif tps >= 13.0:
            color = ColorFormat.YELLOW
        else:
            color = ColorFormat.RED
            
        for player_name in list(self.plugin.tps_enabled_players):
            player = self.plugin.server.get_player(player_name)
            if not player:
                self.plugin.tps_enabled_players.discard(player_name)
                continue
                
            try:
                ping = getattr(player, 'ping', "N/A")
                player_tps = getattr(player, 'tps', tps) # Endstone doesn't have a distinct client TPS, defaulting to server TPS if missing
                player.send_tip(f"§eServer TPS: {color}{tps:.1f} §8| §ePlayer Ping: §a{ping}ms §8| §ePlayer TPS: {color}{player_tps:.1f}")
            except Exception as e:
                self.plugin.logger.warning(f"TPS Monitor error for {player_name}: {e}")

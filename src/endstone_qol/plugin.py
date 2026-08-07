import json
from pathlib import Path

from endstone.plugin import Plugin
from endstone.event import event_handler, PlayerQuitEvent
from endstone import Player, ColorFormat
from endstone.command import Command, CommandSender

# Import modular features
from .features import (
    ShulkerViewerFeature,
    EntityRadarFeature,
    WailaHudFeature,
    TpsMonitorFeature,
    CauldronConcreteFeature,
    PortalCalculatorFeature
)

class QoLPlugin(Plugin):
    """
    Quality of Life Plugin for Endstone (Modular Architecture)
    Provides toggleable features: Shulker Viewer, Radar, WAILA, TPS, Cauldron Concrete, Portal Calc
    """
    name = "endstone_qol"
    api_version = "0.11"
    
    commands = {
        "radar": {
            "description": "Toggle Entity Radar",
            "usages": ["/radar"]
        },
        "tpsmonitor": {
            "description": "Toggle TPS Monitor",
            "usages": ["/tpsmonitor"]
        },
        "portal": {
            "description": "Calculate Portal Coordinates",
            "usages": ["/portal"]
        },
        "waila": {
            "description": "Toggle WAILA HUD",
            "usages": ["/waila"]
        }
    }
    
    def __init__(self):
        super().__init__()
        self.config_dict = {}
        
        # Player-specific toggles
        self.radar_enabled_players = set()
        self.tps_enabled_players = set()
        self.waila_enabled_players = set()
        
        # Schedulers
        self.radar_task = None
        self.waila_task = None
        self.tps_task = None
        
        # Features Instances
        self.shulker_viewer = None
        self.entity_radar = None
        self.waila_hud = None
        self.tps_monitor = None
        self.cauldron_concrete = None
        self.portal_calculator = None

    def load_config(self):
        self.data_folder_path = Path(self.data_folder)
        self.data_folder_path.mkdir(parents=True, exist_ok=True)
        config_path = self.data_folder_path / "config.json"
        
        default_config = {
            "shulker_viewer": True,
            "entity_radar": True,
            "waila_hud": True,
            "tps_monitor": True,
            "cauldron_concrete": True,
            "portal_calculator": True,
            "cauldron_water_cost_per_stack": True
        }
        
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config_dict = json.load(f)
                    
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in self.config_dict:
                        self.config_dict[key] = value
                        
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(self.config_dict, f, indent=4)
                    
            except Exception as e:
                self.logger.error(f"Failed to load config.json: {e}")
                self.config_dict = default_config
        else:
            self.config_dict = default_config
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(self.config_dict, f, indent=4)
            except Exception as e:
                self.logger.error(f"Failed to save default config.json: {e}")

    def on_enable(self) -> None:
        self.load_config()
        self.register_events(self)
        
        # Initialize features
        self.shulker_viewer = ShulkerViewerFeature(self)
        self.entity_radar = EntityRadarFeature(self)
        self.waila_hud = WailaHudFeature(self)
        self.tps_monitor = TpsMonitorFeature(self)
        self.cauldron_concrete = CauldronConcreteFeature(self)
        self.portal_calculator = PortalCalculatorFeature(self)

        # Register event-driven features
        self.register_events(self.shulker_viewer)
        self.register_events(self.cauldron_concrete)
        
        # Schedule repeating tasks for enabled features
        if self.config_dict.get("entity_radar", True):
            self.radar_task = self.server.scheduler.run_task(self, self.entity_radar.run_loop, period=20)
            
        if self.config_dict.get("waila_hud", True):
            self.waila_task = self.server.scheduler.run_task(self, self.waila_hud.run_loop, period=5)
            
        if self.config_dict.get("tps_monitor", True):
            self.tps_task = self.server.scheduler.run_task(self, self.tps_monitor.run_loop, period=20)
            
        self.logger.info(f"{ColorFormat.GREEN}QoL Plugin enabled. Modular features loaded from config.")

    def on_disable(self) -> None:
        if self.radar_task:
            self.radar_task.cancel()
        if self.waila_task:
            self.waila_task.cancel()
        if self.tps_task:
            self.tps_task.cancel()
            
        self.radar_enabled_players.clear()
        self.tps_enabled_players.clear()
        self.waila_enabled_players.clear()
        
        self.logger.info(f"{ColorFormat.RED}QoL Plugin disabled.")

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent):
        # Clean up memory when players leave
        player_name = event.player.name
        self.radar_enabled_players.discard(player_name)
        self.tps_enabled_players.discard(player_name)
        self.waila_enabled_players.discard(player_name)
        if hasattr(self.shulker_viewer, "_last_interact"):
            self.shulker_viewer._last_interact.pop(player_name, None)

    # -------------------------
    # COMMAND DELEGATION
    # -------------------------
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if not isinstance(sender, Player):
            sender.send_error_message("This command can only be run by a player.")
            return True
            
        player_name = sender.name
        
        if command.name == "radar" and self.config_dict.get("entity_radar", True):
            if player_name in self.radar_enabled_players:
                self.radar_enabled_players.remove(player_name)
                sender.send_message(f"{ColorFormat.RED}Entity Radar disabled.")
            else:
                self.radar_enabled_players.add(player_name)
                sender.send_message(f"{ColorFormat.GREEN}Entity Radar enabled.")
            return True
            
        if command.name == "tpsmonitor" and self.config_dict.get("tps_monitor", True):
            if player_name in self.tps_enabled_players:
                self.tps_enabled_players.remove(player_name)
                sender.send_message(f"{ColorFormat.RED}TPS Monitor disabled.")
            else:
                self.tps_enabled_players.add(player_name)
                sender.send_message(f"{ColorFormat.GREEN}TPS Monitor enabled.")
            return True
            
        if command.name == "waila" and self.config_dict.get("waila_hud", True):
            if player_name in self.waila_enabled_players:
                self.waila_enabled_players.remove(player_name)
                sender.send_message(f"{ColorFormat.RED}WAILA HUD disabled.")
            else:
                self.waila_enabled_players.add(player_name)
                sender.send_message(f"{ColorFormat.GREEN}WAILA HUD enabled.")
            return True
            
        if command.name == "portal" and self.config_dict.get("portal_calculator", True):
            self.portal_calculator.handle_command(sender)
            return True
            
        return False

import math
from endstone.event import event_handler, PlayerInteractEvent

class CauldronConcreteFeature:
    def __init__(self, plugin):
        self.plugin = plugin

    @event_handler
    def on_player_interact(self, event: PlayerInteractEvent):
        if not self.plugin.config_dict.get("cauldron_concrete", True):
            return
            
        try:
            player = event.player
            item = event.item
            event_block = event.block
            
            if not event_block:
                return
            
            x, y, z = math.floor(event_block.x), math.floor(event_block.y), math.floor(event_block.z)
            
            # Fetch the live block from the dimension to ensure block states are accurate
            block = player.dimension.get_block_at(x, y, z)
            
            if "cauldron" not in str(block.type).lower():
                return
            
            # Since Endstone 0.11 doesn't support block.states, we MUST use commands.
            # We use 'execute if block' because unlike 'testforblock', it fails silently without spamming the console with ERROR logs.
            cauldron_level = 0
            for i in range(6, 0, -1):
                # We run 'testfor' on the player as the success payload. It will print one INFO log when found, but zero errors!
                cmd = f'execute positioned {x} {y} {z} if block ~ ~ ~ cauldron ["cauldron_liquid"="water","fill_level"={i}] run testfor "{player.name}"'
                
                if self.plugin.server.dispatch_command(self.plugin.server.command_sender, cmd):
                    cauldron_level = i
                    break

            if cauldron_level > 0 and item and "concrete_powder" in str(item.type).lower():
                # Convert the concrete powder to concrete
                event.is_cancelled = True
                count = item.amount
                new_type = str(item.type).replace("_powder", "")
                
                # Replace the item in the player's hand
                self.plugin.server.dispatch_command(
                    self.plugin.server.command_sender,
                    f'clear "{player.name}" {str(item.type).replace("minecraft:", "")} 0 {count}'
                )
                self.plugin.server.dispatch_command(
                    self.plugin.server.command_sender,
                    f'give "{player.name}" {new_type.replace("minecraft:", "")} {count}'
                )
                
                # Deduct cauldron water level
                if self.plugin.config_dict.get("cauldron_water_cost_per_stack", True):
                    stacks_to_consume = math.ceil(count / 64)
                    new_fill = max(0, cauldron_level - stacks_to_consume)
                    
                    self.plugin.server.dispatch_command(
                        self.plugin.server.command_sender,
                        f'setblock {x} {y} {z} cauldron ["fill_level"={new_fill}, "cauldron_liquid"="water"]'
                    )
                    
        except Exception as e:
            self.plugin.logger.error(f"Error in on_player_interact (Cauldron): {e}")

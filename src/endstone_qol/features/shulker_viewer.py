import time
from endstone.event import event_handler, PlayerInteractEvent, PacketReceiveEvent, EventPriority
from endstone import Player

try:
    from chest_form_api_endstone import ChestForm
except ImportError:
    ChestForm = None

class ShulkerViewerFeature:
    def __init__(self, plugin):
        self.plugin = plugin
        self._last_interact = {}
        self._active_forms = {}

    @event_handler
    def on_player_interact(self, event: PlayerInteractEvent):
        if not self.plugin.config_dict.get("shulker_viewer", True) or not ChestForm:
            return

        if "RIGHT_CLICK" not in str(event.action):
            return

        player = event.player
        if not player.is_sneaking:
            return
        item = event.item

        if not item or "shulker_box" not in str(item.type).lower():
            return

        now = time.time()
        if now - self._last_interact.get(player.name, 0) < 1.0:
            event.is_cancelled = True
            return

        # Reset interaction cooldown
        self._last_interact[player.name] = now
        event.is_cancelled = True

        # EXTRACT NBT SYNCHRONOUSLY
        # Extracting item.nbt asynchronously inside the form callback causes a use-after-free Segfault
        # because the 'item' C++ proxy is destroyed after the PlayerInteractEvent finishes!
        nbt_data_dict = {}
        if getattr(item, 'nbt', None):
            try:
                nbt_data_dict = item.nbt.to_dict()
            except Exception as e:
                self.plugin.logger.warning(f"Could not parse Shulker NBT synchronously: {e}")

        self._open_chest_form(player, nbt_data_dict)

    def _open_chest_form(self, player: Player, nbt_data_dict: dict):
        try:
            if not player.is_valid:
                return

            form = ChestForm(self.plugin, "Shulker Box Contents")
            self._active_forms[player.name] = form

            # We must assign an empty callback to the slots, otherwise the form acts weirdly
            def read_only_callback(p: Player, clicked_slot: int):
                # When a slot is clicked, the client natively closes the UI.
                # To make it read-only, we immediately resend the form.
                return self._open_chest_form(p, nbt_data_dict)

            # Fill empty slots (9-44) with blank tiles to prevent UI rendering issues
            for border_slot in range(9, 45):
                form.set_slot(border_slot, "minecraft:black_stained_glass_pane", read_only_callback, item_amount=1, display_name="§8")

            # Fill first row (0-8) and last row (45-53) with End Crystals
            for border_slot in range(0, 9):
                form.set_slot(border_slot, "minecraft:end_crystal", read_only_callback, item_amount=1, display_name="§d✦")
            for border_slot in range(45, 54):
                form.set_slot(border_slot, "minecraft:end_crystal", read_only_callback, item_amount=1, display_name="§d✦")

            if nbt_data_dict:
                try:
                    if "Items" in nbt_data_dict:
                        items_array = nbt_data_dict["Items"]
                        for nbt_item in items_array:
                            slot = int(nbt_item.get("Slot", 0))
                            item_id = str(nbt_item.get("Name", "minecraft:air"))
                            
                            # Bedrock format might use 'Count', but for display ID is enough
                            if item_id != "minecraft:air":
                                count_tag = nbt_item.get("Count", 1)
                                count = int(count_tag.value) if hasattr(count_tag, 'value') else int(count_tag)
                                form.set_slot(slot + 9, item_id, read_only_callback, item_amount=count)
                except Exception as e:
                    self.plugin.logger.warning(f"Could not load Shulker NBT into UI: {e}")

            form.send_to(player)

        except Exception as e:
            self.plugin.logger.error(f"Failed to open Shulker Viewer: {e}")
            player.send_error_message("Could not open Shulker Box Viewer.")

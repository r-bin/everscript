"""Dynamic map inclusion and room slot allocation patch.

Called via #patch("map('path/to/blob.bin', 'name')")
"""


def patch(context, blob_path: str, name: str):
    """
    Args:
        context: CodeGen / compiler instance.
        blob_path: Path to the room blob file.
        name: Name alias for the room (e.g. 'test').
    """
    # Allocate next freed map_key from MemoryManager (e.g. 0x25)
    allocated_key = context.linker.memory_manager.allocate_map_key()
    new_room_id = allocated_key.index

    # Assign the name to this room_id, and register the blob
    context.register_named_map(name, new_room_id, str(blob_path))


run = patch
main = patch

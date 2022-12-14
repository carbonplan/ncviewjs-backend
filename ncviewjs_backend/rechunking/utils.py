def determine_chunk_size(spatial_chunk_square_size: int = 256, target_size_bytes: int = 5e5) -> int:
    return round(target_size_bytes / 4 / spatial_chunk_square_size**2)

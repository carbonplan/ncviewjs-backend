def determine_chunk_size(
    spatial_chunk_square_size: int = 128, target_size_bytes: int = 5e5
) -> int:  # ex 500 KB
    return round((target_size_bytes / 4) / (128 * 128))

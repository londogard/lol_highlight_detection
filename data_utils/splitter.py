import numpy as np
from sklearn.model_selection import train_test_split


def chunk_splitter(total_size: int, chunk_size: int, split: int | float) -> np.array:
    _, val_idxs = train_test_split(
        np.arange(total_size // chunk_size), test_size=split, random_state=42
    )  # ignoring final unsized chunk
    is_valid = np.zeros(total_size, dtype="int")

    for index in val_idxs:
        index *= chunk_size
        is_valid[index : index + chunk_size] = 1

    return is_valid

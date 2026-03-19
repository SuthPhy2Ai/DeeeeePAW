# Copyright (c) 2023, MASSACHUSETTS INSTITUTE OF TECHNOLOGY
# Subject to FAR 52.227-11 - Patent Rights - Ownership by the Contractor (May 2014).
from deepaw.data.layer import pad_and_stack


def collate_list_of_dicts(list_of_dicts, pin_memory=False):
    """
    Collate a list of dictionaries into a single dictionary with batched tensors.

    Args:
        list_of_dicts: List of dictionaries with tensor values
        pin_memory: Whether to pin memory for GPU transfer

    Returns:
        Dictionary with batched tensors
    """
    # Convert from "list of dicts" to "dict of lists"
    dict_of_lists = {k: [d[k] for d in list_of_dicts] for k in list_of_dicts[0]}

    # Convert each list of tensors to single tensor with pad and stack
    if pin_memory:
        pin = lambda x: x.pin_memory()
    else:
        pin = lambda x: x

    collated = {}
    for k, v in dict_of_lists.items():
        if k not in ["filename", "load_time"]:
            collated[k] = pin(pad_and_stack(v))
        else:
            collated[k] = v

    return collated

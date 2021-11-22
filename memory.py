from copy import deepcopy


def cache(data, key, cache_dict, imperative):
    if imperative == 1:
        cache_dict[key] = data
    elif imperative == 2:
        cache_dict[key] = deepcopy(data)
    elif imperative != 0:
        print(f"unknown cache imperative the item {data} will not be cached")

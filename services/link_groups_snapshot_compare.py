import json
from utils.helpers import read_json
from utils.logger import log_entry_exit

@log_entry_exit
def compare_items(item1, item2, ignored_attributes, parent_key=''):
    differences = []
    keys = set(item1.keys()).union(item2.keys())
    for key in keys:
        full_key = f"{parent_key}.{key}" if parent_key else key
        if full_key in ignored_attributes:
            continue
        val1 = item1.get(key)
        val2 = item2.get(key)
        if isinstance(val1, dict) and isinstance(val2, dict):
            nested_differences = compare_items(val1, val2, ignored_attributes, full_key)
            if nested_differences:
                differences.extend(nested_differences)
        elif isinstance(val1, list) and isinstance(val2, list):
            if val1 != val2:
                differences.append(full_key)
        elif val1 != val2:
            differences.append(full_key)
    return differences

@log_entry_exit
def compare_json(snapshot1_file, snapshot2_file, ignored_attributes):
    snapshot1_data = read_json(snapshot1_file)
    snapshot2_data = read_json(snapshot2_file)

    link_groups_1 = {f"{link_group['linkGroupId']['linkGroupCode']}": link_group for link_group in snapshot1_data['snapshot']}
    link_groups_2 = {f"{link_group['linkGroupId']['linkGroupCode']}": link_group for link_group in snapshot2_data['snapshot']}
    
    diff_items = []
    for link_group_id, group_1 in link_groups_1.items():
        if link_group_id in link_groups_2:
            group_2 = link_groups_2[link_group_id]
            diff_attributes = compare_items(group_1, group_2, ignored_attributes)
            if diff_attributes:
                diff_items.append({"linkGroupCode": link_group_id, "attributes": ", ".join(diff_attributes)})
        else:
            diff_items.append({"linkGroupCode": link_group_id, "attributes": "linkGroupCode missing in second snapshot"})

    return {
        "count": len(diff_items),
        "differences": diff_items
    }

@log_entry_exit
def link_groups_compare(original_snapshot_path, modified_snapshot_path, ignored_attributes):
    result = compare_json(original_snapshot_path, modified_snapshot_path, ignored_attributes)
    return result
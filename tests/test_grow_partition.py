from src.partitionaid.operations.grow_partition import grow_logical_partition, grow_physical_partition

#TODO: Mock function to return set value for now.
#       - Later test in a virtual environment or something

def test_grow_logical_pass(monkeypatch):
    partition_info = ["sda4", "1000204886016", "part", "/boot"]
    partition = "/dev/sda4"
    size_increase = "500M"
    backup = True

    def mock_successful_return():
        return {"success": True, "new_partition_size": int(partition_info[1]) / (1024 ** 2)}

    monkeypatch.setattr("src.partitionaid.operations.grow_partition.grow_logical_partition", mock_successful_return)

    result = grow_logical_partition(partition_info, partition, size_increase, backup)

    assert result == {"success": True, "new_partition_size": int(partition_info[1]) / (1024 ** 2)}


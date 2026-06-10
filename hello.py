print("Hello, World!")


def sort_array(arr: list[int]) -> list[int]:
    """使用快速排序算法对 int 列表进行排序（升序）"""
    if len(arr) <= 1:
        return arr

    # 选取基准值（pivot），这里选中间位置的元素
    pivot = arr[len(arr) // 2]

    # 分区：小于、等于、大于基准值
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    # 递归排序左右子数组并合并
    return sort_array(left) + middle + sort_array(right)


# 测试用例
if __name__ == "__main__":
    test_data = [3, 6, 8, 10, 1, 2, 1]
    print(f"排序前: {test_data}")
    print(f"排序后: {sort_array(test_data)}")

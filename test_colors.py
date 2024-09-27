def fill_missing_integers(lst, start, end):
    """
    Fill the list with all missing integers between `start` and `end` (inclusive).
    
    Args:
    - lst (list): A list of integers.
    - start (int): The start of the range.
    - end (int): The end of the range.
    
    Returns:
    - filled_list (list): The list filled with the missing integers.
    """
    # Create a set of all integers in the range [start, end]
    complete_set = set(range(start, end + 1))
    
    # Find the missing integers by subtracting the given list from the complete set
    missing_integers = complete_set - set(lst)
    
    # Add the missing integers to the original list
    filled_list = lst + list(missing_integers)
    
    return filled_list

# Example usage:
lst = [2, 1]
filled_lst = fill_missing_integers(lst, 0, 4)
print(filled_lst)  # Output: [0, 1, 2, 3, 4]

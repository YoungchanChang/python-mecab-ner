

def subs_str_finder(str_range, str_pattern):
    """
    str_range에서 part_str 찾기
    :param str_range: 문자열
    :param part_str: 찾는 문자열 패턴
    :return: 문자열이 위치한 시작, 끝 인덱스
    """

    sub_len = len(str_pattern)

    while str_pattern in str_range:
        first_index = str_range.find(str_pattern)
        second_index = first_index + sub_len
        return first_index, second_index


def delete_pattern_from_string(string, pattern, index, nofail=False):
    """ 문자열에서 패턴을 찾아서 *로 변환해주는 기능 """

    # raise an error if index is outside of the string
    if not nofail and index not in range(len(string)):
        raise ValueError("index outside given string")

    # if not erroring, but the index is still not in the correct range..
    if index < 0:  # add it to the beginning
        return pattern + string
    if index > len(string):  # add it to the end
        return string + pattern

    len_pattern = len(pattern)

    pattern_list = pattern.split()

    # 토큰이 하나인 경우에 대한 처리
    if len(pattern_list) == 1:
        blank_pattern = len(pattern) * "*"
        # insert the new string between "slices" of the original
        return string[:index] + blank_pattern + string[index + len_pattern:]

    # 토큰에 space가 포함된 경우에 대한 처리
    for pattern_item in pattern_list:
        pattern_length = len(pattern_item)
        blank_pattern = pattern_length * "*"
        string = string[:index] + blank_pattern + string[index + pattern_length:]
        index += (pattern_length + 1)
    return string


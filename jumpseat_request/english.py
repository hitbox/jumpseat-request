def english_list(sliceable, conjunction='and', separator=', '):
    sliceable = list(sliceable)
    return f'{separator.join(sliceable[:-1])} {conjunction} {sliceable[-1]}'

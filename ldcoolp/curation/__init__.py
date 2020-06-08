def df_to_dict_single(df):
    """
    Purpose:
      Convert a single entry pandas DataFrame into a dictionary and strip out
      indexing information

    :param df: pandas DataFrame with single entry (e.g., use df.loc[] to filter)

    :return df_dict: dict that contains single entry pandas DF
    """
    df_dict = df.reset_index().to_dict(orient='records')[0]
    return df_dict

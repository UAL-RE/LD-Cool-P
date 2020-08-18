def df_to_dict_single(df, curation_id=None):
    """
    Purpose:
      Convert a single entry pandas DataFrame into a dictionary and strip out
      indexing information
    :param df: pandas DataFrame with single entry (e.g., use df.loc[] to filter)
    :param curation_id: integer providing the curation_id. Default: Uses most recent
    :return df_dict: dict that contains single entry pandas DF
    """

    df_dict = df.reset_index().to_dict(orient='records')

    if isinstance(curation_id, type(None)):
        # Uses most recent (reverse ordered)
        df_dict0 = df_dict[0]
    else:
        # Use specified curation_id
        df_dict0 = [sub_dict for sub_dict in df_dict if sub_dict['id'] == curation_id][0]

    return df_dict0

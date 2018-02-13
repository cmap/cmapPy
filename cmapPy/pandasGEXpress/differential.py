import cmapPy.math.robust_zscore as zscore

def prep_mats(df, plate_control=True, group_field='pert_type', group_val='ctl_vehicle'):

    # Calculate level 4 data from level 3

    if plate_control == False:
        neg_dex = df.col_metadata_df[df.col_metadata_df[group_field] == group_val].index.tolist()
        neg_df = df.data_df[neg_dex]
        zscore_data = zscore(df.data_df, neg_df)

    elif plate_control == True:
        zscore_data = zscore(df.data_df)

    row_metadata_df = df.row_metadata_df

    # Threshold zscore data before returning
    zscore_data[zscore_data < -10] = -10
    zscore_data[zscore_data > 10] = 10

    # These sortings might be unnecessary now with updates to GCToo
    zscore_data.sort_index(inplace=True)
    row_metadata_df.sort_index(inplace=True)
    zscore_gctoo = GCToo.GCToo(data_df=zscore_data, row_metadata_df=row_metadata_df, col_metadata_df=df.col_metadata_df)

    return zscore_gctoo
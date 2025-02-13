"""
    Helper script to format pandas dataframe to markdown
"""

import pandas
from tabulate import tabulate


def dataframe_to_markdown(data: pandas.DataFrame):
    """
    Process a pandas dataframe into markdown.

    Parameters
    ----------
    data :  pandas.DataFrame
        Dataframe to be formatted.

    Returns
    -------
    str
        markdown string format of dataframe.
    """
    try:
        markdown_table = tabulate(
            data, headers="keys", tablefmt="grid", showindex=False, maxcolwidths=60
        )
    except Exception as error:
        markdown_table = tabulate(
            data,
            headers="keys",
            tablefmt="grid",
            showindex=False,
        )
    markdown_table = f"\n {markdown_table} \n"
    return markdown_table
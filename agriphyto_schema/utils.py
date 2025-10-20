from pandas.api.types import is_numeric_dtype


def clean_varname(var_name: str | float) -> str:

    """
    Clean variable name by replacing special characters.
    """
    if is_numeric_dtype(type(var_name)):
        var_name = str(var_name)
    var_name = var_name.replace("*", "star")
    var_name = var_name.replace(" ", "_")
    var_name = var_name.replace("-", "_")
    var_name = var_name.replace(";", "_")
    var_name = var_name.replace("<", "_")
    var_name = var_name.replace(">", "_")
    var_name = var_name.replace("(", "")
    var_name = var_name.replace(")", "")
    var_name = var_name.replace("\xa0", "_")
    return var_name
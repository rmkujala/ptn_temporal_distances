import pickle


def get_data_or_compute(fname, comp_func, recompute=False, *args, **kwargs):
    """
    Parameters
    ----------
    fname : str
        path to where store the data
    comp_func : callable
        the function for which to compute values
    recompute : bool
    args:
        positional arguments to be passed to comp_func
    kwargs:
        keyword arguments to be passed to comp_func


    Returns
    -------
    data: object
        the data object returned by comp_fund
    """
    try:
        if recompute:
            raise RuntimeError("Recompute!")
        with open(fname, "rb") as f:
            data = pickle.load(f)
    except (RuntimeError, TypeError, EOFError) as e:
        print(e)
        with open(fname, "wb") as f:
            data = comp_func(*args, **kwargs)
            pickle.dump(data, f, -1)
    return data

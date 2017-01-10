import pickle
import multiprocessing


def run_in_parallel(work_func, arg_list, n_cpus, chunksize=1):
    """
    Run ``work_func(args)`` with n_cpus number of processors in parallel
    Parameters
    ----------
    work_func : callable object (function)
    arg_list : list-like
        list of lists containing the input arguments
    n_cpus : int
        number of cpus
    chunksize: int
        how many tasks are give for a pool
    Returns
    -------
    result_list : list
        [work_func(args) for args in arg_list]
    """
    if n_cpus == "max":
        n_cpus = multiprocessing.cpu_count()
    # mainly for debugging purposes and generality
    if n_cpus == 1:
        result_list = []
        for args in arg_list:
            result_list.append(work_func(args))
    else:
        pool = multiprocessing.Pool(processes=n_cpus)
        result_list = \
            pool.map_async(work_func, arg_list, chunksize=chunksize).get(31536000)
    return result_list


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

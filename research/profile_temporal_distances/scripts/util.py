# -*- coding: latin-1 -*-
import pickle
import multiprocessing

import smopy


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


def split_into_equal_length_parts(array, n_splits):
    # http://stackoverflow.com/questions/2130016/splitting-a-list-of-arbitrary-size-into-only-roughly-n-equal-parts
    # pretty nice :)
    a = array
    n = n_splits
    k, m = divmod(len(a), n)
    lists = [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
    assert(lists[0][0] == array[0])
    assert(lists[-1][-1] == array[-1])
    return lists

def make_filename_nice(fname):
    fname = fname.replace(" ", "_")
    fname = fname.replace("'", "")
    fname = fname.replace("ä", "a")
    fname = fname.replace("ö", "o")
    return fname

def make_string_latex_friendly(fname):
    fname = fname.replace("_", "\\_")
    fname = fname.replace("'", "\'")
    fname = fname.replace("ä", '\\\"a')
    fname = fname.replace("ö", '\\"o')
    return fname

def get_data_or_compute(fname, comp_func, *args, **kwargs):
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
    recompute = kwargs.pop('recompute', False)

    try:
        if recompute:
            raise RuntimeError("Recompute!")
        with open(fname, "rb") as f:
            data = pickle.load(f)
    except (RuntimeError, TypeError, EOFError, IOError) as e:
        print("Data not found, computing; error message was:" + str(e))
        with open(fname, "wb") as f:
            data = comp_func(*args, **kwargs)
            pickle.dump(data, f, -1)
    return data


def _get_smopy_map(lat_min, lat_max, lon_min, lon_max, z):
    args = (lat_min, lat_max, lon_min, lon_max, z)
    if args not in _get_smopy_map.maps:
        smopy.Map.get_allowed_zoom = lambda self, z: z
        _get_smopy_map.maps[args] = smopy.Map((lat_min, lon_min, lat_max, lon_max), z=z)
    return _get_smopy_map.maps[args]
_get_smopy_map.maps = {}

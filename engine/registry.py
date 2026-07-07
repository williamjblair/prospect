"""Maps a dataset name to its checker. Adding a dataset = adding a line here."""
from .checkers.marson_perturbseq import MarsonPerturbseqChecker

_CHECKERS = {
    "marson": MarsonPerturbseqChecker,
}

def get_checker(dataset: str, data_path: str):
    if dataset not in _CHECKERS:
        raise ValueError(f"unknown dataset '{dataset}'. known: {list(_CHECKERS)}")
    return _CHECKERS[dataset](data_path)

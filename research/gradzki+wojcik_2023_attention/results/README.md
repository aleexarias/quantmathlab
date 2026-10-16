# Results

Predictions of the trained models, written by `training/train.py` and read
by the notebook. They are committed, so building the documentation never
needs to train.

One file per pair and bar length, `<pair>_<minutes>.csv`, with a row for
each window of the validation (2020) and test (2021) sets:

| Column | Meaning |
| --- | --- |
| `time` | Start of the window's last bar, on the paper's clock (histdata.com's plus six hours) |
| `set` | `validation` or `test` |
| `probability` | Predicted probability that the next close is higher |

Is Attention All You Need for Intraday Forex Trading?
=====================================================

:Paper: :cite:t:`gradzki+wojcik_2023_attention`
:Journal: *Expert Systems*, 41, 2023
:DOI: `10.1111/exsy.13317 <https://doi.org/10.1111/exsy.13317>`__
:Link: `ResearchGate <https://www.researchgate.net/publication/370255323_Is_attention_all_you_need_for_intraday_Forex_trading>`__
:Status: In progress.

Can the architecture behind today's language models read a currency chart?
:cite:t:`gradzki+wojcik_2023_attention` sit a Transformer in front of six
currency pairs and ask it the same question every hour, or every two, four,
eight or twelve: will the next bar close higher or lower?

Paper's Findings
----------------

- As classifiers, the Transformer and its strongest benchmark, a ResNet-LSTM,
  are evenly matched over the 30 pairs and bar lengths: the Transformer has the
  best accuracy 16 times and the best AUROC 13 times, the ResNet-LSTM 13 and
  16. The Transformer's accuracies range from 0.49 to 0.60: better than a coin,
  but not by much.
- Trading on the predictions makes money on paper for EURCHF, USDJPY, EURGBP
  and USDCHF, most reliably with bars of four hours or longer. EURUSD, the most
  traded pair and so the most efficient, is also the noisiest, and the model
  does not perform well on it. On EURPLN the model is accurate, but the pair's
  wide spread eats the gain.
- Costs decide the outcome: one EURCHF strategy ends the year at 110.7 without
  costs, 105.2 with a 2-pip spread and 99.9 with a 4-pip one.
- High accuracy can mislead. For EURCHF at 60 minutes, the vast majority of
  correct predictions fall between 21:00 and midnight, when spreads widen
  several-fold, and a naive rule that knows only the hour of the day does as
  well. Without those hours, the profits vanish.
- In a sensitivity analysis on EURCHF, the length of the input window, 24, 48
  or 96 bars, makes no consistent difference, but without its
  technical-analysis features the model stays at chance level.

Notebook
--------

The :doc:`notebook <gradzki+wojcik_2023_attention>` replicates the paper
for the series its warning rests on: EURCHF at 60, 120 and 720 minutes,
and USDJPY at 60 minutes.

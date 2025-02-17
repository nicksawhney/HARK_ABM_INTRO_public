from sharkfin.utilities import *
import math
import numpy as np

class FinanceModel:
    """
    A class representing the financial system in the simulation.

    Contains parameter values for:
      - the capital gains expectations function
      - the dividend
      - the risky asset expectations

    Contains data structures for tracking ROR and STD over time.
    """

    # Empirical data
    sp500_ror = 0.000628
    sp500_std = 0.011988

    # Simulation parameter
    days_per_quarter = 60

    # Expectation calculation parameters
    p1 = 0.1
    delta_t1 = 30

    a = -math.log(p1) / delta_t1

    p2 = 0.1
    delta_t2 = 60

    b = math.log(p2) / delta_t2

    # Quarterly dividend rate and standard deviation.
    dividend_ror = 0.03
    dividend_std = 0.01

    # Data structures. These will change over time.
    starting_price = 100
    prices = None
    ror_list = None

    expected_ror_list = None
    expected_std_list = None

    def add_ror(self, ror):
        self.ror_list.append(ror)
        asset_price = self.prices[-1] * (1 + ror)
        self.prices.append(asset_price)
        return asset_price

    def __init__(
        self,
        dividend_ror=None,
        dividend_std=None,
        p1=None,
        p2=None,
        delta_t1=None,
        delta_t2=None,
    ):

        if dividend_ror:
            self.dividend_ror = dividend_ror

        if dividend_std:
            self.dividend_std = dividend_std

        if p1:
            self.p1 = p1

        if p2:
            self.p2 = p2

        if delta_t1:
            self.delta_t1 = delta_t1

        if delta_t2:
            self.delta_t2 = delta_t2

        self.prices = [self.starting_price]
        self.ror_list = []
        self.expected_ror_list = []
        self.expected_std_list = []

    def asset_price_stats(self):
        price_stats = {}

        price_stats['min_asset_price'] = min(self.prices)
        price_stats['max_asset_price'] = max(self.prices)

        price_stats['idx_min_asset_price'] = np.argmin(self.prices)
        price_stats['idx_max_asset_price'] = np.argmax(self.prices)

        price_stats['mean_asset_price'] = np.mean(self.prices)
        price_stats['std_asset_price'] = np.std(self.prices)

        return price_stats

    def calculate_risky_expectations(self):
        """
        Compute the quarterly expectations for the risky asset based on historical return rates.

        In this implementation there are a number of references to:
          - paramters that are out of scope
          - data structures that are out of scope

        These should be bundled together somehow.

        NOTE: This MUTATES the 'expected_ror_list' and so in current design
        has to be called on a schedule... this should be fixed.
        """
        # note use of data store lists for time tracking here -- not ideal
        D_t = sum([math.exp(self.a * (l + 1)) for l in range(len(self.ror_list))])
        S_t = math.exp(
            self.b * (len(self.prices) - 1)
        )  # because p_0 is included in this list.

        w_0 = S_t
        w_t = [
            (1 - S_t) * math.exp(self.a * (t + 1)) / D_t
            for t in range(len(self.ror_list))
        ]

        expected_ror = w_0 * self.sp500_ror + sum(
            [w_ror[0] * w_ror[1] for w_ror in zip(w_t, self.ror_list)]
        )
        self.expected_ror_list.append(expected_ror)

        expected_std = math.sqrt(
            w_0 * pow(self.sp500_std, 2)
            + sum(
                [
                    w_ror_er[0] * pow(w_ror_er[1] - expected_ror, 2)
                    for w_ror_er in zip(w_t, self.ror_list)
                ]
            )
        )
        self.expected_std_list.append(expected_std)

    def rap(self):
        """
        Returns the current risky asset price.
        """
        return self.prices[-1]

    def risky_expectations(self):
        """
        Return quarterly expectations for the risky asset.
        These are the average and standard deviation for the asset
        including both capital gains and dividends.
        """
        # expected capital gains quarterly
        ex_cg_q_ror = ror_quarterly(self.expected_ror_list[-1], self.days_per_quarter)
        ex_cg_q_std = sig_quarterly(self.expected_std_list[-1], self.days_per_quarter)

        # factor in dividend:
        cg_w_div_ror, cg_w_div_std = combine_lognormal_rates(
            ex_cg_q_ror, ex_cg_q_std, self.dividend_ror, self.dividend_std
        )

        market_risky_params = {'RiskyAvg': 1 + cg_w_div_ror, 'RiskyStd': cg_w_div_std}

        return market_risky_params

    def reset(self):
        """
        Reset the data stores back to original value.
        """
        self.prices = [100]
        self.ror_list = []

        self.expected_ror_list = []
        self.expected_std_list = []
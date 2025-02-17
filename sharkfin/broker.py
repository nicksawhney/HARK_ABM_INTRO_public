class Broker:
    """
    A share Broker. Collects orders from agents, then trades on the market
    and reports a rate of return.

    Parameters
    ----------
    market - a MarketPNL instance
    """

    buy_limit = 0
    sell_limit = 0

    # track the buy/sell orders due to macro updates separately
    # this data won't go to sim_stats yet but will be used for investigating
    # the mechanism
    buy_orders_macro = 0
    sell_orders_macro = 0

    buy_sell_history = None
    buy_sell_macro_history = None

    market = None

    def __init__(self, market):
        self.market = market
        self.buy_sell_history = []
        self.buy_sell_macro_history = []

    def transact(self, delta_shares, macro=False):
        """
        Input: an array of share deltas. positive for buy, negative for sell.

        macro: True if the transactions are from a 'macro update' step.
        """
        self.buy_limit += delta_shares[delta_shares > 0].sum()
        self.sell_limit += -delta_shares[delta_shares < 0].sum()

        if macro:
            self.buy_orders_macro += delta_shares[delta_shares > 0].sum()
            self.sell_orders_macro += -delta_shares[delta_shares < 0].sum()

    def trade(self, seed=None):
        """
        Broker executes the trade on the financial market and then updates
        their record of the current asset price.

        Input: (optional) random seed for the simulation
        Output: Rate of return of the asset value that day.
        """

        # use integral shares here.
        buy_sell = (int(self.buy_limit), int(self.sell_limit))
        self.buy_sell_history.append(buy_sell)

        buy_sell_macro = (int(self.buy_orders_macro), int(self.sell_orders_macro))
        self.buy_sell_macro_history.append(buy_sell_macro)
        # print("Buy/Sell Limit: " + str(buy_sell))

        self.market.run_market(buy_sell=buy_sell, seed=seed)

        # clear the local limits
        self.buy_limit = 0
        self.sell_limit = 0

        self.buy_orders_macro = 0
        self.sell_orders_macro = 0

        return buy_sell, self.market.daily_rate_of_return()

    def close(self):
        self.market.close_market()

        
# flake8: noqa
from vnpy.event import EventEngine
from time import sleep

from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp
import vnpy_crypto
vnpy_crypto.init()


from vnpy_binance import (
    BinanceSpotGateway
)

from vnpy_fufi import (
    FufiSpotGateway
)

from vnpy_market_making import MarketMakingApp
from order_copier_algo import OrderCopierAlgo


def main():
    """"""
    qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)

    main_engine.add_gateway(BinanceSpotGateway)
    main_engine.add_gateway(FufiSpotGateway)

    
    algo_engine = main_engine.add_app(MarketMakingApp)
    algo_engine.init_engine()    

    sleep(10)
    algo_engine.load_algo_template()

    main_engine.write_log("MM策略全部初始化")
    sleep(60)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()

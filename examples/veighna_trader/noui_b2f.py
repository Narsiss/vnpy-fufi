# flake8: noqa

import multiprocessing
import sys
from time import sleep
from datetime import datetime, time
from logging import INFO

from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine

import vnpy_crypto
vnpy_crypto.init()

from vnpy.trader.constant import (
    Direction,
    Offset,
    Exchange
)

from vnpy_binance import (
    BinanceSpotGateway
)

from vnpy_fufi import (
    FufiSpotGateway
)

from vnpy_market_making import MarketMakingApp

SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True

#import your account private key here
fufi_setting = {
    "account": "",
    "private_key": "",
    "chain_node": "https://test-chain.ambt.art",
    "server": "https://dapp-dex-dev.ambt.art/",
    "ws_server": "wss://amax-dex-dev.ambt.art/socket.io",
    "asset_contract": "amax.mtoken",
    "trade_pair": "METH_MUSDT",
    "dex_contract": "dexv3",
    "proxy_host": "",
    "proxy_port": 0,
}

#import your key secret here
binance_setting = {
    "key": "",
    "secret": "",
    "服务器": "REAL",
    "代理地址": "127.0.0.1",
    "代理端口": 7890
}



def check_trading_period():
    """"""
    return True


def run_child():
    """
    Running in the child process.
    """
    SETTINGS["log.file"] = True

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(FufiSpotGateway)
    main_engine.add_gateway(BinanceSpotGateway)
    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register("FUFI_USDT_NOUI", log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    main_engine.connect(fufi_setting, "FUFI_SPOT")
    main_engine.write_log("连接Fufi接口")

    main_engine.connect(binance_setting, "BINANCE_SPOT")
    main_engine.write_log("连接Binance接口")


    sleep(10)

    algo_engine = main_engine.add_app(MarketMakingApp)
    algo_engine.init_engine()
    main_engine.write_log("MM引擎初始化完成")

    sleep(30)

    print(main_engine.get_contract("1.LOCAL"))

    algo_engine.load_algo_template()
    main_engine.write_log("MM策略全部初始化")

    algo_name = algo_engine.start_algo(
        template_name="DepthCopierAlgo",
        vt_symbols=["ethusdt.BINANCE","1.LOCAL"],
        direction=Direction.LONG,
        offset=Offset.NONE,
        price=0,
        volume=0,
        setting={
            "display_volume": 0.0,
            "interval": 10,
            "copy_from": "ethusdt.BINANCE",
            "parse_to": "METH_MUSDT.FUFI_SPOT",
            "from_vt_symbol": "ethusdt.BINANCE",
            "to_vt_symbol": "1.LOCAL"
        }
    )

    main_engine.write_log(f"{algo_name}策略启动")

    while True:
        sleep(10)
        trading = check_trading_period()
        if not trading:
            print("关闭子进程")
            main_engine.close()
            sys.exit(0)

def run_parent():
    """
    Running in the parent process.
    """
    print("启动Fufi守护进程")

    child_process = None

    while True:
        trading = check_trading_period()

        # Start child process in trading period
        if trading and child_process is None:
            print("启动子进程")
            child_process = multiprocessing.Process(target=run_child)
            child_process.start()
            print("子进程启动成功")

        # 非记录时间则退出子进程
        if not trading and child_process is not None:
            if not child_process.is_alive():
                child_process = None
                print("子进程关闭成功")

        sleep(5)


if __name__ == "__main__":
    run_parent()
import pandas as pd
from backtesting import Backtest
from strategy import RangoMananaVolumen
from clear_data import filtrar_horario_mercado_ny, auditar_tiempo_y_duplicados

if __name__ == "__main__":

    ruta_original   = "datos_historicos/SPY_M1.csv"
    df_spy          = filtrar_horario_mercado_ny(ruta_csv = ruta_original, save_like_csv = False)
    df_spy_auditado = auditar_tiempo_y_duplicados(df_spy)


    df_spy_auditado['timestamp_ny'] = pd.to_datetime(df_spy_auditado['timestamp_ny'])

    df_spy_auditado = df_spy_auditado.set_index('timestamp_ny')
    df_spy_auditado = df_spy_auditado.drop(columns=['timestamp'])
    df_spy_auditado = df_spy_auditado.rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low', 
        'close': 'Close', 'volume': 'Volume'
    })
    df_spy_auditado.index = df_spy_auditado.index.tz_localize(None)

    bt      = Backtest(df_spy_auditado, RangoMananaVolumen, cash = 100000, commission = 0.0002)
    stats   = bt.run()
    
    print(stats)
    bt.plot(open_browser = True)
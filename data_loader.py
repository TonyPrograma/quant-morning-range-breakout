from huggingface_hub import hf_hub_download
import pandas as pd
from pathlib import Path

carpeta_salida = Path("datos_historicos")
carpeta_salida.mkdir(exist_ok = True) # Crea la carpeta si no existe

# The dataset is updated monthly. We set the final month to March 2026.
# If you run this in the future, you can extend 'final_year' and 'final_month'.

start_year  = 2019
final_year  = 2026
final_month = 11

meses = [f"ohlcv_{year}-{month:02d}.parquet" 
         for year in range(start_year, final_year + 1) 
         for month in range(1, 13) 
         if not (year == 2026 and month > final_month)]  

tickers_interes = ["SPY", "META", "TSLA"]
datos_por_ticker = {ticker: [] for ticker in tickers_interes}

print("Iniciando descarga... esto puede tardar un poco.")

for mes in meses:
    archivo = f"data/{mes}"
    
    try:
        # Intentamos descargar el archivo mensual
        ruta_local = hf_hub_download(
            repo_id="mito0o852/OHLCV-1m",
            filename=archivo,
            repo_type="dataset"
        )
        
        df_mes = pd.read_parquet(path=ruta_local, columns=["timestamp", "ticker", "open", "high", "low", "close", "volume"])
        
        for ticker in tickers_interes:
            df_ticker = df_mes[df_mes["ticker"] == ticker]
            
            if not df_ticker.empty:
                df_ticker = df_ticker.drop(columns=["ticker"])
                datos_por_ticker[ticker].append(df_ticker)
                
        print(f"✅ {mes} procesado")
        
    except Exception as e:
        print(f"⚠️ Saltando {mes}: Archivo no disponible en el servidor.")
        continue # Le dice a Python: "pasa al siguiente mes inmediatamente"


print("\n💾 Guardando archivos CSV...")

for ticker, lista_dataframes in datos_por_ticker.items():
    if lista_dataframes:

        df_final = pd.concat(lista_dataframes, ignore_index=True)
        df_final = df_final.sort_values("timestamp").reset_index(drop=True)
        ruta_csv = carpeta_salida / f"{ticker}_M1.csv"

        df_final.to_csv(ruta_csv, index=False)
        
        print(f"✅ {ticker}: {len(df_final):,} filas guardadas en {ruta_csv}")
    else:
        print(f"⚠️ No se encontraron datos para {ticker}")

print("\n¡Proceso terminado!")
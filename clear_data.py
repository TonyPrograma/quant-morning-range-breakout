from pathlib import Path
import pandas as pd
import pandas_market_calendars as mcal


def filtrar_horario_mercado_ny(
    ruta_csv: str, 
    open_market: str = '09:30', 
    close_market: str = '16:00', 
    save_like_csv: bool = True, 
    new_path: str = 'datos_filtrados_ny'
) -> pd.DataFrame:
    
    """
    Lee un archivo CSV, convierte a hora NY, filtra horario regular.
    Identifica y reporta los Half-Days, pero NO los elimina.
    """
    print(f"Cargando datos desde: {ruta_csv}...")

    df = pd.read_csv(ruta_csv)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    ts_ny           = df['timestamp'].dt.tz_convert('America/New_York')

    hora        = ts_ny.dt.time
    hora_inicio = pd.Timestamp(open_market).time()
    hora_fin    = pd.Timestamp(close_market).time()
    mascara     = (hora >= hora_inicio) & (hora < hora_fin)
    
    df_filtrado = df[mascara].copy()
    df_filtrado['timestamp_ny'] = ts_ny[mascara]
    df_filtrado = df_filtrado.reset_index(drop=True)
    
    print(f"✅ Datos filtrados inicialmente: {len(df_filtrado):,} filas.")


    nyse        = mcal.get_calendar('NYSE')
    fecha_min   = df_filtrado['timestamp_ny'].dt.date.min().strftime('%Y-%m-%d')
    fecha_max   = df_filtrado['timestamp_ny'].dt.date.max().strftime('%Y-%m-%d')


    schedule        = nyse.schedule(start_date = fecha_min, end_date = fecha_max)
    early_closes    = nyse.early_closes(schedule = schedule)
    half_days       = early_closes.index.strftime('%Y-%m-%d').tolist()
    

    fecha_actual = df_filtrado['timestamp_ny'].dt.strftime('%Y-%m-%d')
    es_half_day  = fecha_actual.isin(half_days)
    
    if es_half_day.any():
        print(f"\n📅 ALERTA: Se identificaron {len(half_days)} días de medio día (Half-Days) en el dataset.")
        print("   (Estos días NO han sido eliminados. Solo se reportan para auditoría).")
        reporte_half_days = df_filtrado[es_half_day].groupby(fecha_actual[es_half_day]).size()
        print("\n   Detalle de velas por cada Half-Day encontrado:")
        print(f"   {'Fecha':<12} | {'Velas':<15}")
        print("   " + "-" * 30)
        for fecha, conteo in reporte_half_days.items():
            print(f"   {fecha:<12} | {conteo:<15,}")


    df_limpio = df_filtrado.copy() 


    if save_like_csv:
        carpeta_destino = Path(new_path)
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        nombre_sin_extension = Path(ruta_csv).stem
        
        nuevo_nombre    = f"{nombre_sin_extension}_NY_Limpio.csv"
        ruta_guardado   = carpeta_destino / nuevo_nombre
        
        df_limpio.to_csv(ruta_guardado, index=False)
        print(f"💾 Archivo guardado en: {ruta_guardado}")

    return df_limpio




def verificar_integridad_ohlcv(df: pd.DataFrame) -> pd.DataFrame:

    print(f"\n🕵️‍♂️ Verificando integridad de datos")
    columnas_ohlcv  = ['open', 'high', 'low', 'close', 'volume']
    nulos           = df[columnas_ohlcv].isnull().sum()
    menores_cero    = (df[columnas_ohlcv] <= 0).sum()

    if nulos.sum() == 0 and menores_cero.sum() == 0:
        print("✅ ¡Datos impecables! No hay nulos, ni ceros, ni negativos.")
    else:
        print("⚠️ ¡Se encontraron anomalías imposibles en los datos!")
    return df



def auditar_tiempo_y_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina duplicados, detecta huecos y los clasifica, pero NO elimina días.
    Solo retorna el DataFrame con los duplicados corregidos.
    """
    print(f"\n⏱️ Analizando continuidad del tiempo ({len(df):,} filas)...")


    df_ordenado         = df.sort_values('timestamp_ny').reset_index(drop = True)
    duplicados_count    = df_ordenado.duplicated(subset = ['timestamp_ny'], keep = 'first').sum()
    df_ordenado         = df_ordenado.drop_duplicates(subset = ['timestamp_ny'], keep = 'first').reset_index(drop = True)


    if duplicados_count > 0:
        print(f"🧹 Se eliminaron {duplicados_count} filas con timestamps duplicados (conservando la primera).")
    else:
        print("✅ Sin timestamps duplicados.")


    df_ordenado['diferencia_tiempo'] = df_ordenado['timestamp_ny'].diff()


    mismo_dia = df_ordenado['timestamp_ny'].dt.date == df_ordenado['timestamp_ny'].shift(1).dt.date
    es_hueco  = (df_ordenado['diferencia_tiempo'] > pd.Timedelta(minutes = 1)) & mismo_dia
    huecos    = df_ordenado[es_hueco].copy()

    
    if not huecos.empty:
        huecos['minutos_faltantes'] = (huecos['diferencia_tiempo'].dt.total_seconds() / 60) - 1

        fechas_panico = [
            '2020-03-09', '2020-03-12', '2020-03-16', '2020-03-18',
            '2023-03-10', '2023-03-13', '2023-03-14'
        ]
        
        def clasificar_gap(row):
            fecha_str = row['timestamp_ny'].strftime('%Y-%m-%d')
            minutos   = row['minutos_faltantes']
            
            if fecha_str in fechas_panico:
                return "🔴 Pánico"
            elif minutos >= 15:
                return "🟠 Glitch (Grave)"
            elif minutos >= 2:
                return "🟡 Glitch (Leve)"
            else:
                return "🟢 Micro-Gap"


        huecos['clasificacion'] = huecos.apply(clasificar_gap, axis = 1)
        huecos['ultimo_dato']   = huecos['timestamp_ny'] - huecos['diferencia_tiempo']

        print(f"\n⚠️ Se detectaron {len(huecos)} huecos de tiempo intra-día.")

        print(f"{'Desde (Último Dato)':<22} | {'Hasta (Dato Recuperado)':<22} | {'Faltan':<8} | {'Clasificación'}")
        print("-" * 95)
        
        # Iteramos sobre cada hueco individual para imprimir sus fechas exactas
        for _, row in huecos.iterrows():
            desde_str = row['ultimo_dato'].strftime('%Y-%m-%d %H:%M:%S')
            hasta_str = row['timestamp_ny'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"{desde_str:<22} | {hasta_str:<22} | {int(row['minutos_faltantes']):<8} | {row['clasificacion']}")

        total_faltantes = int(huecos['minutos_faltantes'].sum())
        print(f"\n🕒 Total histórico de datos faltantes detectados: {total_faltantes:,} minutos.")

    
        mask_panico         = huecos['clasificacion'].str.contains("Pánico")
        minutos_glitches    = huecos[~mask_panico]['minutos_faltantes'].sum()
        minutos_validos     = len(df_ordenado) + minutos_glitches
        

        if minutos_validos > 0:
            calidad_pct = (len(df_ordenado) / minutos_validos) * 100
        else:
            calidad_pct = 0.0


        print(f"✅ CALIDAD DEL DATASET: {calidad_pct:.4f}%")


    else:
        print("✅ El tiempo es continuo. No hay huecos intra-día.")

    # Limpiamos las columnas temporales usadas para el análisis
    df_ordenado = df_ordenado.drop(columns = ['diferencia_tiempo'], errors = 'ignore').reset_index(drop = True)
    return df_ordenado



if __name__ == "__main__":
    ruta_original = "datos_historicos/SPY_M1.csv"
    
    df_spy = filtrar_horario_mercado_ny(ruta_csv = ruta_original, save_like_csv = False)
    verificar_integridad_ohlcv(df_spy)

    df_spy_auditado = auditar_tiempo_y_duplicados(df_spy)
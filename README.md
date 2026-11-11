## 📊 Data Pipeline & Download / Pipeline de Datos y Descarga

### 🇬🇧 English
Data Source: Historical 1-minute OHLCV data for SPY, META, and TSLA is automatically downloaded from the Hugging Face dataset mito0o852/OHLCV-1m.

How to download:

1. Ensure you have installed the dependencies (pip install -r requirements.txt).
2. Run the data_loader.py script. This will create the datos_historicos/ folder and download the .parquet files month by month. If you want to download other assets, add the assets to the list on line 20 of the code.
3. Run clear_data.py to filter the data to New York regular market hours (handling DST automatically) and discard early closing days (Half-Days). in clear_data.py, line 185 specifies that it only runs for the S&P 500. If you want to run it for other assets, change the path to the desired CSV file.

Forensic Data Audit:
The cleaning pipeline includes a detailed analysis printed in the terminal. It detects and classifies "Gaps" (missing data), identifying whether they were caused by actual market panic events (e.g., S&P 500 Circuit Breakers in 2020 and 2023, where the exchange halted trading for minutes) or data provider glitches. With this, the script calculates a Data Quality Score (99.78%) and identifies the exact missing minutes in OHLCV.
Important note: By design, no days are removed from the final dataset for backtesting, thus preserving the historical integrity.

Data Availability Limit:
As of today, the public dataset is updated monthly and contains data up to March 2026. If you run the script after this date, it will automatically fetch the most recently available data. If the script requests a month that is not yet on the server, it will safely skip it (404 error handling).

Note: Raw CSV files are not included in this repository due to GitHub size limits. The code is 100% reproducible.


Backtest Execution:
To evaluate the strategy, the run_backtest.py script acts as the project's main orchestrator. When executed, the following happens:

1. Data Preparation: It loads the clean data, sets the timestamp as the index, and formats the OHLCV columns required by the engine.
2. Simulation: It initializes the backtesting.py engine with the RangoMananaVolumen class, applying risk management and commissions. By default, it runs simulations on the S&P 500; if you want to run simulations on a different asset, change the path (to the CSV file) for that asset on line 8 of the code.
3. Metrics: It prints a complete statistical report to the console (Sharpe Ratio, Max Drawdown, Profit Factor, number of trades, etc.).
4. Visualization: It generates and opens an interactive chart in the browser with candlesticks, moving averages, and entry/exit arrows for each trade.

How to run it: python run_backtest.py


Strategy Documentation:
To deeply understand the trading strategy's logic, operational rules, and mathematical foundations, a technical document in PDF format is included.

This document details:

The exact definition of the morning range and breakout conditions.
The historical volume filter and its statistical justification.
Risk management rules (Position Sizing) and exit parameters (TP/SL).

### ⚙️ Prerequisites
- **Python 3.14.3** or higher.
- Virtual environment (recommended).

---



### 🇪🇸 Español

Fuente de Datos: Los datos históricos de 1 minuto (OHLCV) para SPY, META y TSLA se descargan automáticamente del dataset de Hugging Face mito0o852/OHLCV-1m.

Cómo descargarlos:

1. Asegúrate de tener instaladas las dependencias (pip install -r requirements.txt).
2. Ejecuta el script data_loader.py. Esto creará la carpeta datos_historicos/ y descargará los archivos .parquet mes por mes. Si quiere descargar otros activos, en la línea de codigo 20, agrega los activos en la lista. 
3. Ejecuta clear_data.py para filtrar los datos al horario regular de mercado de Nueva York (manejando el DST automáticamente) y descartar los días de cierre anticipado (Half-Days). clear_data.py, en la línea de codigo 185, se detalla que solo corre para S&P500. SSi quieres correr otros activos, cambia a la ruta del CSV que desa.

Auditoría Forense de Datos:
El pipeline de limpieza incluye un análisis detallado que se imprime en la terminal. Este detecta y clasifica los "Gaps" (pérdidas de datos), identificando si fueron causados por eventos reales de pánico en el mercado (ej. los Circuit Breakers del S&P 500 en 2020 y 2023, donde la bolsa cerró minutos) o por fallos del proveedor de datos. Con esto, el script calcula un Data Quality Score (99.78%) e identifica los minutos exactos faltantes en OHLCV.
Nota importante: Por diseño, no se elimina ningún día del dataset final para el backtesting, preservando así la integridad del histórico.

Límite de disponibilidad de datos:
A la fecha, el dataset público se actualiza mensualmente y contiene datos hasta marzo de 2026. Si ejecutas el script después de esta fecha, buscará automáticamente los datos más recientes disponibles. Si el script solicita un mes que aún no está en el servidor, lo saltará de forma segura (manejo de errores 404).

Nota: Los archivos CSV crudos no están incluidos en este repositorio debido a los límites de tamaño de GitHub. El código es 100% reproducible.


Ejecución del Backtest:
Para evaluar la estrategia, el script run_backtest.py actúa como el orquestador principal del proyecto. Al ejecutarlo, ocurre lo siguiente:

1. Preparación de Datos: Carga los datos limpios, establece el índice de tiempo (timestamp) y formatea las columnas OHLCV requeridas por el motor.
2. Simulación: Inicializa el motor de backtesting.py con la clase RangoMananaVolumen, aplicando la gestión de riesgo y las comisiones. Por defecto simula en el S&P 500, si quieres que simule en otro activo, en la linea de codigo 8, cambia a la ruta (CSV) del activo. 
3. Métricas: Imprime en consola un reporte estadístico completo (Sharpe Ratio, Max Drawdown, Profit Factor, número de operaciones, etc.).
4. Visualización: Genera y abre un gráfico interactivo en el navegador con las velas japonesas, las medias y las flechas de entrada/salida de cada operación.


Cómo ejecutarlo: python run_backtest.py


Documentación de la Estrategia:
Para comprender a fondo la lógica de la estrategia de trading, las reglas operativas y los fundamentos matemáticos detrás de la estrategia, se adjunta un documento técnico en formato PDF.

En este documento se detallan:

La definición exacta del rango matutino y las condiciones de ruptura.
El filtro de volumen histórico y su justificación estadística.
Las reglas de gestión de riesgo (Position Sizing) y los parámetros de salida (TP/SL).


### ⚙️ Requisitos Previos
- **Python 3.14.3** o superior.
- Entorno virtual (recomendado).

---
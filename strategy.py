import pandas as pd
from backtesting import Strategy
from collections import deque

class RangoMananaVolumen(Strategy):


    hora_inicio_rango   = '09:30'
    TimeFrame_Range     = '5min'
    dias_historial      = 14     
    operar_hasta        = '13:00'
    min_perc_vol        = 100
    fixed_risk          = 100
    take_profit_RR      = 2
    max_risk_size       = 10
    


    def init(self):

        dt_inicio   = pd.to_datetime(f"2000-01-01 {self.hora_inicio_rango}")
        dt_fin      = dt_inicio + pd.Timedelta(self.TimeFrame_Range)

        self.str_inicio     = dt_inicio.strftime('%H:%M')
        self.str_fin        = dt_fin.strftime('%H:%M')
        self.str_fin_op     = pd.to_datetime(f"2000-01-01 {self.operar_hasta}").strftime('%H:%M')

        df_m1       = self.data.df.copy()
        self.df_m5  = df_m1.resample(self.TimeFrame_Range).agg({
            'Open': 'first',  
            'High': 'max',     
            'Low': 'min',      
            'Close': 'last',   
            'Volume': 'sum'    
        }).dropna()            


        def calcular_volumen_rango(serie_volumen):

            horas   = serie_volumen.index.strftime('%H:%M')
            mascara = (horas >= self.str_inicio) & (horas < self.str_fin)
            return serie_volumen[mascara].sum()

    
        self.df_Daily = df_m1.resample('1D').agg({
                        'Open': 'first',  
                        'High': 'max',     
                        'Low': 'min',      
                        'Close': 'last',   
                        'Volume': calcular_volumen_rango 
                    }).dropna()

        self.df_Daily['Vol_Average'] = self.df_Daily['Volume'].rolling(window = self.dias_historial).mean().shift(1)

        self.fecha_actual       = None
        self.permit_oper_today  = False
        self.operado_hoy        = False
        self.high_value         = 0
        self.low_value          = 0
        self.type_oper          = None
        



    def next(self):

        fecha_actual    = self.data.index[-1].date()
        hora_str        = self.data.index[-2].strftime('%H:%M')


        if hora_str == self.str_fin and fecha_actual != self.fecha_actual:
            self.permit_oper_today  = False
            self.fecha_actual       = fecha_actual
            self.operado_hoy        = False
            self.high_value         = 0
            self.low_value          = 0
            self.type_oper          = None

            fecha_dt = pd.to_datetime(fecha_actual)

            if fecha_dt in self.df_Daily.index:
                vol_promedio = self.df_Daily.loc[fecha_dt, 'Vol_Average']
                
                if pd.isna(vol_promedio):
                    vol_promedio = 0.0 
            else:
                vol_promedio = 0.0

            fecha_actual_m1         = self.data.index[-1]
            hora_inicio_m5_actual   = fecha_actual_m1.floor(self.TimeFrame_Range)
            hora_m5_anterior        = hora_inicio_m5_actual - pd.Timedelta(self.TimeFrame_Range)
            
            if hora_m5_anterior in self.df_m5.index:
                vol_m5_anterior = self.df_m5.loc[hora_m5_anterior, 'Volume']
            else:
                vol_m5_anterior = 0.0

            if float(vol_promedio) > 0 and (100.0 * float(vol_m5_anterior) / float(vol_promedio)) >= self.min_perc_vol:
                self.permit_oper_today  = True
                self.high_value         = self.df_m5.loc[hora_m5_anterior, 'High']
                self.low_value          = self.df_m5.loc[hora_m5_anterior, 'Low']
                cierre                  = float(self.df_m5.loc[hora_m5_anterior, 'Close'])
                apertura                = float(self.df_m5.loc[hora_m5_anterior, 'Open'])

                if cierre < apertura:      
                    self.type_oper = 'Sell'
                elif cierre > apertura:    
                    self.type_oper = 'Buy'
                else:                      
                    self.type_oper = 'None'


        #---------Cierra por estás fuera del horario operacional -----------------
        if hora_str >= self.str_fin_op:
            self.permit_oper_today  = False
            self.high_value         = 0
            self.low_value          = 0
            self.type_oper          = None

            if self.position:
                self.position.close()


        #---------Momento para operar -----------------
        if hora_str > self.str_fin and hora_str < self.str_fin_op:
            if self.permit_oper_today and not self.position and not self.operado_hoy  and self.type_oper != None:

                if self.type_oper == 'Buy' and float(self.data.Open[-2]) <= float(self.high_value)  and float(self.data.Close[-2]) > float(self.high_value) :
                    size        = int(self.fixed_risk / abs(self.data.Open[-1] - self.low_value)) 
                    stop_loss   = self.low_value
                    take_profit = self.data.Open[-1] + (float(self.take_profit_RR) * abs(self.data.Open[-1] - self.low_value))

                    if size > 10 : 
                        size = self.max_risk_size

                    if size >= 1 :
                        self.buy(size = size, sl = stop_loss, tp = take_profit)
                        self.operado_hoy = True 


                if self.type_oper == 'Sell' and float(self.data.Open[-2]) >= float(self.low_value)  and float(self.data.Close[-2]) < float(self.low_value) :
                    size        = int(self.fixed_risk / abs(self.high_value - self.data.Open[-1])) 
                    stop_loss   = self.high_value 
                    take_profit = self.data.Open[-1] - (float(self.take_profit_RR) * abs(self.high_value - self.data.Open[-1]))

                    if size > 10 : 
                        size = self.max_risk_size

                    if size >= 1 :
                        self.sell(size = size, sl = stop_loss, tp = take_profit)
                        self.operado_hoy = True 

            





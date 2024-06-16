import talib
import pandas as pd

def calculate_macd(ohlcv_data):
    """Calculates MACD, signal line, and histogram."""
    macd, signal, hist = talib.MACD(ohlcv_data['close'])
    return macd, signal, hist

def calculate_ichimoku_cloud(ohlcv_data):
    """Calculates Ichimoku Cloud components."""
    tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span = talib.ICHIMOKU(ohlcv_data['high'], ohlcv_data['low'])
    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span

def calculate_moving_averages(ohlcv_data):
    """Calculates moving averages: short, long, 29-day, and 200-day."""
    short_ma = talib.SMA(ohlcv_data['close'], timeperiod=7)
    long_ma = talib.SMA(ohlcv['close'], timeperiod=21)
    ma_29 = talib.SMA(ohlcv['close'], timeperiod=29)
    ma_200 = talib.SMA(ohlcv['close'], timeperiod=200)
    return short_ma, long_ma, ma_29, ma_200

def analyze_volume(ohlcv_data, timeframe='1d'):
    """Analyzes volume data to detect spikes."""
    volume = ohlcv_data['volume']  # Fetch recent volume data
    current_volume = volume[-1]
    avg_volume = np.mean(volume[:-1])  
    volume_spike_threshold = 2 if timeframe == '5m' else 1.5  # Different thresholds for different timeframes
    volume_spike = current_volume > volume_spike_threshold * avg_volume
    return volume_spike

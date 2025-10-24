import numpy as np

def compute_metrics(values):
    returns = np.diff(values) / values[:-1]
    total_return = (values[-1] / values[0]) - 1
    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
    max_drawdown = np.min(values / np.maximum.accumulate(values) - 1)

    return {
        'total_return': round(float(total_return), 4),
        'sharpe_ratio': round(float(sharpe), 2),
        'max_drawdown': round(float(max_drawdown), 4)
    }
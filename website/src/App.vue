<template>
  <div class="backtest-container">
    <h2>Backtest Simulator</h2>

    <form @submit.prevent="runBacktest" class="form">
      <label>
        Ticker:
        <input v-model="ticker" placeholder="AAPL" />
      </label>

      <label>
        Strategy:
        <select v-model="strategy">
          <option value="momentum">Momentum</option>
          <option value="reversal">Reversal</option>
        </select>
      </label>

      <label>
        SMA Period:
        <input type="number" v-model.number="smaPeriod" />
      </label>

      <label>
        Start Date:
        <input type="date" v-model="startDate" />
      </label>

      <label>
        End Date:
        <input type="date" v-model="endDate" />
      </label>

      <button type="submit">Run Backtest</button>
    </form>

    <div v-if="loading">Loading...</div>

    <div class="resultsbox">
      <div id="chart-container"></div>

      <div v-if="metrics" class="results">
        <h3>Backtest Metrics:</h3>
        <ul>
          <li>Total Return: {{ metrics.total_return * 100 }}%</li>
          <li>Sharpe Ratio: {{ metrics.sharpe_ratio }}</li>
          <li>Max Drawdown: {{ metrics.max_drawdown * 100 }}%</li>
        </ul>
      </div>

      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { CandlestickSeries, ColorType, createChart, LineSeries } from 'lightweight-charts'
import type { IChartApi, ISeriesApi, LineData } from 'lightweight-charts'

const ticker = ref('AAPL')
const strategy = ref('momentum')
const smaPeriod = ref(20)
const startDate = ref('2023-01-01')
const endDate = ref('2024-01-01')

const error = ref<string | null>(null)
const loading = ref(false)

interface EquityLinePoint {
  date: string
  value: number
}
interface EquityCandlestickPoint {
  time: string
  open: number,
  high: number,
  low: number,
  close: number
}

interface Metrics {
  total_return: number
  sharpe_ratio: number
  max_drawdown: number
}

interface ApiResponse {
  metrics: Metrics
  equity_curve: EquityLinePoint[]
  candlestick_data: EquityCandlestickPoint[]
}

const metrics = ref<Metrics | null>(null)

let chart: IChartApi | null = null
let lineSeries: ISeriesApi<'Line'> | null = null
let candlestickSeries: ISeriesApi<'Candlestick'> | null = null

const runBacktest = async () => {
  loading.value = true
  error.value = null
  if (chart) {
    chart.remove()
    chart = null
    lineSeries = null
  }

  try {
    const response = await axios.post<ApiResponse>('http://127.0.0.1:5000/api/backtest', {
      ticker: ticker.value,
      strategy: strategy.value,
      start_date: startDate.value,
      end_date: endDate.value,
      params: { sma_period: smaPeriod.value },
    })

  metrics.value = response.data.metrics

  console.log(response.data)



  chart = createChart('chart-container', {
    width: 800,
    height: 600,
    layout: {
      background: { type: ColorType.Solid, color: '#0120100' },
      textColor: '#00FFFF',
    },
  })
  lineSeries = chart.addSeries(LineSeries)
  candlestickSeries = chart.addSeries(CandlestickSeries)

  const formattedLineData: LineData[] = response.data.equity_curve.map((point) => ({
    time: point.date as unknown as string,
    value: point.value,
  }))

  lineSeries.setData(formattedLineData)
  candlestickSeries.setData(response.data.candlestick_data)


  chart.timeScale().fitContent();

  } catch (err: unknown) {
    if (axios.isAxiosError(err)) {
      error.value = err.response?.data?.message ?? err.message
    } else if (err instanceof Error) {
      error.value = err.message
    } else {
      error.value = String(err)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.backtest-container {
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: sans-serif;
}

.resultsbox {
  margin-top: 20px;
  display: flex;
  flex-direction: row;
}

.form label {
  display: block;
  margin-bottom: 10px;
}

button {
  margin-top: 10px;
  padding: 5px 10px;
  background-color: #4caf50;
  border-radius: 4px;
  border: none;
  color: white;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
  scale: 1.02;
}

.results {
  margin-top: 20px;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>

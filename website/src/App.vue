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
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { createChart, LineSeries } from 'lightweight-charts'
import type { IChartApi, ISeriesApi, LineData } from 'lightweight-charts'

const ticker = ref('AAPL')
const strategy = ref('momentum')
const smaPeriod = ref(20)
const startDate = ref('2023-01-01')
const endDate = ref('2024-01-01')

const error = ref<string | null>(null)
const loading = ref(false)

interface EquityPoint {
  date: string
  value: number
}

interface Metrics {
  total_return: number
  sharpe_ratio: number
  max_drawdown: number
}

interface ApiResponse {
  metrics: Metrics
  equity_curve: EquityPoint[]
}

const metrics = ref<Metrics | null>(null)

let chart: IChartApi | null = null
let lineSeries: ISeriesApi<'Line'> | null = null

const runBacktest = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await axios.post<ApiResponse>('http://127.0.0.1:5000/api/backtest', {
      ticker: ticker.value,
      strategy: strategy.value,
      start_date: startDate.value,
      end_date: endDate.value,
      params: { sma_period: smaPeriod.value },
    })

  metrics.value = response.data.metrics

  if (chart) {
    chart.remove()
    chart = null
    lineSeries = null
  }

  chart = createChart("chart-container", { width: 800, height: 600 })
  lineSeries = chart.addSeries(LineSeries)

  const formattedData: LineData[] = response.data.equity_curve.map((point) => ({
    time: point.date as unknown as string,
    value: point.value,
  }))

  lineSeries.setData(formattedData)

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
  max-width: 500px;
  margin: auto;
  font-family: sans-serif;
}

.form label {
  display: block;
  margin-bottom: 10px;
}

button {
  margin-top: 10px;
  padding: 5px 10px;
}

.results {
  margin-top: 20px;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>

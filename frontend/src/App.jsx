import { useEffect, useState } from 'react'
import {
  Activity, ArrowDownRight, ArrowUpRight, BarChart3, BookOpen, Check,
  ChevronDown, CircleHelp, CloudSun, Gauge, GitCompareArrows, Leaf,
  LoaderCircle, Menu, Microscope, Wind, X,
} from 'lucide-react'
import {
  CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8001'
const CITY_CHOICES = ['Ahmedabad', 'Amritsar', 'Bengaluru', 'Chennai', 'Delhi', 'Hyderabad', 'Jaipur', 'Kolkata', 'Lucknow', 'Mumbai', 'Pune', 'Surat']
const NAV = [
  { id: 'forecast', label: 'Forecast', icon: Gauge },
  { id: 'transfer', label: 'City transfer', icon: GitCompareArrows },
  { id: 'explain', label: 'What drives it', icon: BarChart3 },
  { id: 'method', label: 'Method notes', icon: BookOpen },
]

const AQI_FIELDS = [
  ['aqi_today', 'Today'],
  ['aqi_lag_1', 'Yesterday'],
  ['aqi_lag_2', '2 days ago'],
  ['aqi_lag_3', '3 days ago'],
  ['aqi_lag_4', '4 days ago'],
  ['aqi_lag_5', '5 days ago'],
  ['aqi_lag_6', '6 days ago'],
  ['aqi_lag_7', '7 days ago'],
]

const DEMO_VALUES = {
  aqi_history: [96, 103, 109, 112, 117, 120, 124],
}

async function api(path, options) {
  const response = await fetch(`${API}${path}`, options)
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(body.detail || 'The API could not complete this request.')
  return body
}

function EmptyState({ icon: Icon = Activity, title, detail }) {
  return <div className="empty-state"><span className="empty-icon"><Icon size={19} /></span><strong>{title}</strong><p>{detail}</p></div>
}

function Stat({ label, value, note, icon: Icon }) {
  return <div className="stat"><div className="stat-top"><span>{label}</span><Icon size={16} /></div><strong>{value}</strong><small>{note}</small></div>
}

function TrendChart({ points, comparisonPoints = [], comparisonName, forecast, rangeDays = 30 }) {
  if (!points?.length) return <EmptyState icon={Activity} title="No city history yet" detail="Add the city-day dataset to data/raw to populate this timeline." />
  const visiblePoints = points.slice(-rangeDays)
  const comparisonByDate = new Map(comparisonPoints.slice(-rangeDays).map((point) => [point.date, point.aqi]))
  const chartPoints = visiblePoints.map((point) => ({ ...point, comparison: comparisonByDate.get(point.date) ?? null }))
  const values = [...visiblePoints.map((point) => point.aqi), ...comparisonPoints.slice(-rangeDays).map((point) => point.aqi)]
  const low = Math.floor(Math.min(...values) / 50) * 50
  const high = Math.ceil(Math.max(...values) / 50) * 50 || 50
  return <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%">
    <LineChart data={chartPoints} margin={{ top: 14, right: 12, left: -18, bottom: 4 }}>
      <CartesianGrid stroke="#e1e4dc" vertical={false} />
      <XAxis dataKey="date" tickFormatter={(value) => value.slice(5)} tickLine={false} axisLine={false} minTickGap={34} />
      <YAxis domain={[low, high]} tickLine={false} axisLine={false} />
      <Tooltip contentStyle={{ border: '1px solid #dfe3d9', borderRadius: 4, fontSize: 12 }} formatter={(value, name) => [Number(value).toFixed(1), name]} labelFormatter={(value) => `Observed · ${value}`} />
      {forecast != null && <ReferenceLine y={forecast} stroke="#f27658" strokeDasharray="5 5" label={{ value: 'Forecast', fill: '#ad4d36', fontSize: 11, position: 'insideTopRight' }} />}
      <Line name={points[0]?.city || 'Selected city'} type="monotone" dataKey="aqi" stroke="#176b60" strokeWidth={2.5} dot={false} activeDot={{ r: 4, fill: '#f27658', stroke: '#f3f4ee' }} />
      {comparisonPoints.length > 0 && <Line name={comparisonName || 'Comparison'} type="monotone" dataKey="comparison" stroke="#e47a4d" strokeWidth={2} strokeDasharray="5 4" dot={false} activeDot={{ r: 4 }} connectNulls />}
    </LineChart>
  </ResponsiveContainer></div>
}

function App() {
  const [page, setPage] = useState('forecast')
  const [city, setCity] = useState('Ahmedabad')
  const [compareCity, setCompareCity] = useState('Delhi')
  const [compareHistory, setCompareHistory] = useState([])
  const [rangeDays, setRangeDays] = useState(30)
  const [cities, setCities] = useState([])
  const [apiState, setApiState] = useState('checking')
  const [history, setHistory] = useState([])
  const [forecast, setForecast] = useState(null)
  const [matrix, setMatrix] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [mobileNav, setMobileNav] = useState(false)
  const [pipelineMode, setPipelineMode] = useState('live')
  const [live, setLive] = useState(null)
  const [liveLoading, setLiveLoading] = useState(false)
  const [liveError, setLiveError] = useState('')
  const [liveHistoryLoading, setLiveHistoryLoading] = useState(false)
  const [form, setForm] = useState({ aqi_history: [] })
  const [transferMode, setTransferMode] = useState('live')
  const [transferSourceCity, setTransferSourceCity] = useState('Delhi')
  const [transferTargetCity, setTransferTargetCity] = useState('Surat')
  const [liveTransferResult, setLiveTransferResult] = useState(null)
  const [liveTransferBusy, setLiveTransferBusy] = useState(false)
  const [liveTransferError, setLiveTransferError] = useState('')
  const comparisonCity = cities.find((item) => item.toLowerCase() === compareCity.toLowerCase() && item.toLowerCase() !== city.toLowerCase()) || cities.find((item) => item.toLowerCase() !== city.toLowerCase()) || ''

  async function runLiveTransfer() {
    setLiveTransferBusy(true)
    setLiveTransferError('')
    try {
      const data = await api(`/live-transfer/${encodeURIComponent(transferSourceCity)}/${encodeURIComponent(transferTargetCity)}`)
      setLiveTransferResult(data)
    } catch (err) {
      setLiveTransferError(err.message || 'Could not complete live cross-city transfer.')
    } finally {
      setLiveTransferBusy(false)
    }
  }

  function applyDemoInputs() {
    setForm({ aqi_history: DEMO_VALUES.aqi_history })
    setError('')
  }

  function resetInputs() {
    setForm({ aqi_history: [] })
    setForecast(null)
  }

  useEffect(() => {
    api('/health').then((health) => setApiState(health.data_loaded ? (health.model_loaded ? 'ready' : 'needs-model') : 'needs-data')).catch(() => setApiState('offline'))
    api('/cities').then((result) => setCities(result.cities)).catch(() => {})
  }, [])

  useEffect(() => {
    if (!cities.length) return
    if (!cities.some((item) => item.toLowerCase() === city.toLowerCase())) setCity(cities[0])
  }, [cities, city])

  useEffect(() => {
    if (page !== 'forecast' || !cities.length) return
    if (pipelineMode === 'live') {
      setLiveHistoryLoading(true)
      api(`/live-history/${encodeURIComponent(city)}`)
        .then((result) => {
          setHistory(result.observations)
          setForm({ aqi_history: result.observations.map((item) => Number(item.aqi)) })
        })
        .catch(() => {
          // Fallback to historical dataset if live telemetry is unavailable
          api(`/history/${encodeURIComponent(city)}?limit=90`)
            .then((res) => {
              setHistory(res.observations)
              setForm({ aqi_history: res.observations.slice(-7).map((item) => Number(item.aqi)) })
            })
            .catch(() => setHistory([]))
        })
        .finally(() => setLiveHistoryLoading(false))
    } else {
      api(`/history/${encodeURIComponent(city)}?limit=90`)
        .then((res) => {
          setHistory(res.observations)
          setForm({ aqi_history: res.observations.slice(-7).map((item) => Number(item.aqi)) })
        })
        .catch(() => setHistory([]))
    }
  }, [city, page, cities, pipelineMode])

  useEffect(() => {
    if (page !== 'forecast') return
    setLive(null)
    setLiveError('')
    setLiveLoading(true)
    let active = true
    api(`/live/${encodeURIComponent(city)}`)
      .then((data) => {
        if (!active) return
        setLive(data)
        setLiveError('')
      })
      .catch((err) => {
        if (!active) return
        setLive(null)
        setLiveError(err.message || 'Live AQI unavailable')
      })
      .finally(() => {
        if (active) setLiveLoading(false)
      })
    return () => { active = false }
  }, [city, page])

  useEffect(() => {
    if (page !== 'forecast' || !comparisonCity) return
    if (pipelineMode === 'live') {
      api(`/live-history/${encodeURIComponent(comparisonCity)}`)
        .then((result) => setCompareHistory(result.observations))
        .catch(() => {
          api(`/history/${encodeURIComponent(comparisonCity)}?limit=90`)
            .then((res) => setCompareHistory(res.observations))
            .catch(() => setCompareHistory([]))
        })
    } else {
      api(`/history/${encodeURIComponent(comparisonCity)}?limit=90`)
        .then((res) => setCompareHistory(res.observations))
        .catch(() => setCompareHistory([]))
    }
  }, [comparisonCity, page, pipelineMode])

  useEffect(() => {
    if (page === 'transfer') {
      if (!matrix) api('/transfer-matrix').then(setMatrix).catch((issue) => setError(issue.message))
      if (!liveTransferResult && !liveTransferBusy) {
        runLiveTransfer()
      }
    }
    if (page === 'explain') api(`/explain/${encodeURIComponent(city)}`).then(setExplanation).catch((issue) => setError(issue.message))
  }, [page, city, matrix])

  async function submitForecast(event) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      const payload = { city }
      if (form.aqi_history.length >= 7) {
        const historyValues = form.aqi_history.map((value) => Number(value))
        payload.aqi_today = historyValues[historyValues.length - 1]
        payload.aqi_lag_1 = historyValues[historyValues.length - 2]
        payload.aqi_lag_2 = historyValues[historyValues.length - 3]
        payload.aqi_lag_3 = historyValues[historyValues.length - 4]
        payload.aqi_lag_4 = historyValues[historyValues.length - 5] ?? null
        payload.aqi_lag_5 = historyValues[historyValues.length - 6] ?? null
        payload.aqi_lag_6 = historyValues[historyValues.length - 7] ?? null
        payload.aqi_lag_7 = historyValues[0]
      }

      setForecast(await api('/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }))
    } catch (issue) { setError(issue.message) }
    finally { setBusy(false) }
  }

  const active = NAV.find((item) => item.id === page)
  const statusLabel = { checking: 'Checking connection', ready: 'Model ready', 'needs-model': 'Dataset connected · model needed', 'needs-data': 'Waiting for dataset', offline: 'API offline' }[apiState]

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNav ? 'sidebar-open' : ''}`}>
      <a className="brand" href="#forecast" onClick={() => setPage('forecast')}><span className="brand-mark"><Wind size={20} strokeWidth={2.1} /></span><span><b>AIR / FIELD</b><small>AQI FORECASTING</small></span></a>
      <div className="project-title"><span className="eyebrow">INDIA AQI</span><p>Daily air<br />quality.</p><span className="side-subtitle">Choose a city<br />and view tomorrow.</span></div>
      <div className="nav-label">WORKSPACE</div>
      <nav className="side-nav" aria-label="Main navigation">{NAV.map(({ id, label, icon: Icon }) => <button key={id} className={page === id ? 'nav-item active' : 'nav-item'} onClick={() => { setPage(id); setMobileNav(false); setError('') }}><Icon size={17} /><span>{label}</span>{page === id && <span className="nav-indicator" />}</button>)}</nav>
      <div className="sidebar-bottom"><div className="source-note"><span className="source-dot" /><span>Live dashboard<small>Forecast for learning and comparison</small></span></div><div className="version">AQI / INDIA <span>v0.1</span></div></div>
    </aside>
    {mobileNav && <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setMobileNav(false)} />}
    <main className="main-area">
      <header className="topbar"><button className="icon-button menu-button" aria-label="Open navigation" onClick={() => setMobileNav(true)}><Menu size={19} /></button><div className="breadcrumb"><span>WORKSPACE</span><span className="crumb-slash">/</span><b>{active?.label.toUpperCase()}</b></div><div className={`connection ${apiState}`}><span className="connection-dot" />{statusLabel}</div></header>
      <div className="page-content">
        {page === 'forecast' && <>
          <section className="page-heading">
            <div>
              <div className="eyebrow green-eyebrow"><span className="tiny-line" /> AIR QUALITY <span className="heading-separator">/</span> INDIA</div>
              <h1>{pipelineMode === 'live' ? 'Live Telemetry, ' : 'Historical AQI, '}<span>with context.</span></h1>
              <p>{pipelineMode === 'live' ? 'Forecasting tomorrow from real-time 7-day sensor telemetry (CPCB NAQI converted).' : 'Evaluating next-day predictions against the held-out historical CPCB dataset.'}</p>
            </div>
            <div className="heading-date">
              <span>PIPELINE MODE</span>
              <b>{pipelineMode === 'live' ? 'Real-Time Telemetry' : 'Historical Benchmark'}</b>
              <small>{pipelineMode === 'live' ? 'Open-Meteo live feed · Nov 2026' : 'Audited CPCB series · 2022–2025'}</small>
            </div>
          </section>

          <div className="pipeline-toggle-bar">
            <span className="toggle-label">FORECAST PIPELINE:</span>
            <div className="toggle-buttons">
              <button
                type="button"
                className={`toggle-btn ${pipelineMode === 'live' ? 'toggle-active' : ''}`}
                onClick={() => setPipelineMode('live')}
              >
                <Activity size={14} /> ⚡ Live Telemetry Pipeline (Nov 2026)
              </button>
              <button
                type="button"
                className={`toggle-btn ${pipelineMode === 'historical' ? 'toggle-active' : ''}`}
                onClick={() => setPipelineMode('historical')}
              >
                <BookOpen size={14} /> 📚 Historical Benchmark (2022–2025)
              </button>
            </div>
          </div>

          {error && <div className="alert"><CircleHelp size={17} /><span>{error}</span><button aria-label="Dismiss" onClick={() => setError('')}><X size={15} /></button></div>}
          <section className="overview-grid">
            <div className="forecast-panel">
              <div className="panel-top">
                <div>
                  <span className="eyebrow">{pipelineMode === 'live' ? 'REAL-TIME TELEMETRY PIPELINE' : 'HISTORICAL BENCHMARK'}</span>
                  <h2>Air quality outlook</h2>
                </div>
                <span className="model-chip"><span /> {apiState === 'ready' ? 'MODEL READY' : 'MODEL UNAVAILABLE'}</span>
              </div>
              <form onSubmit={submitForecast} className="forecast-form">
                <div className="field-block">
                  <label className="field-label" htmlFor="city-select">City</label>
                  <div className="select-wrap"><select id="city-select" value={city} onChange={(event) => { setCity(event.target.value); setExplanation(null) }}>{(cities.length ? cities : CITY_CHOICES).map((name) => <option key={name}>{name}</option>)}</select><ChevronDown size={16} /></div>
                </div>

                <div className="mini-history-card">
                  <div className="mini-history-header">
                    <span className="eyebrow">{pipelineMode === 'live' ? 'LIVE 7-DAY TELEMETRY' : 'AUTO-FILLED AQI'}</span>
                    <span className="mini-badge">{pipelineMode === 'live' ? 'Live CPCB NAQI' : 'Last 7 days'}</span>
                  </div>
                  {liveHistoryLoading ? (
                    <p className="form-hint muted-text"><LoaderCircle className="spin" size={14} /> Loading real-time 7-day telemetry for {city}...</p>
                  ) : form.aqi_history.length ? (
                    <div className="mini-history-values">
                      {form.aqi_history.map((value, index) => (
                        <span key={`${city}-${index}`} className="mini-pill">{value}</span>
                      ))}
                    </div>
                  ) : (
                    <p className="form-hint muted-text"><CircleHelp size={14} /> Loading recent AQI for {city}...</p>
                  )}
                </div>

                <div className="quick-actions">
                  <button type="button" className="secondary-button" onClick={applyDemoInputs}>Try demo values</button>
                  <button type="button" className="ghost-button" onClick={resetInputs}>Reset</button>
                </div>
                {liveLoading ? (
                  <div className="mini-history-card">
                    <div className="mini-history-header">
                      <span className="eyebrow">LIVE CURRENT AQI</span>
                      <span className="mini-badge">Fetching</span>
                    </div>
                    <p className="form-hint muted-text"><LoaderCircle className="spin" size={14} /> Fetching live reading for {city}...</p>
                  </div>
                ) : live ? (
                  <div className="mini-history-card">
                    <div className="mini-history-header">
                      <span className="eyebrow">LIVE CURRENT AQI</span>
                      <span className="mini-badge">{live.scale}</span>
                    </div>
                    <div className="live-reading">
                      <strong>{live.current_aqi}</strong>
                      <span>{live.source}<small>{live.observed_at ? new Date(live.observed_at).toLocaleString('en-IN') : ''}</small></span>
                    </div>
                  </div>
                ) : liveError ? (
                  <div className="mini-history-card">
                    <div className="mini-history-header">
                      <span className="eyebrow">LIVE CURRENT AQI</span>
                      <span className="mini-badge">Unavailable</span>
                    </div>
                    <p className="form-hint muted-text" style={{ margin: 0, fontSize: '11px' }}>
                      <CircleHelp size={13} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} />
                      {liveError}
                    </p>
                  </div>
                ) : null}
                <p className="form-hint"><CircleHelp size={14} /> {pipelineMode === 'live' ? 'Live mode uses real-time 7-day telemetry converted to Indian NAQI.' : 'Historical mode evaluates the model against verified 2022–2025 records.'}</p>
                <button className="primary-button" type="submit" disabled={busy || apiState !== 'ready'}>{busy ? <LoaderCircle className="spin" size={17} /> : <Activity size={17} />}<span>{busy ? 'Estimating…' : 'Estimate next day'}</span><ArrowUpRight size={16} /></button>
                {apiState !== 'ready' && <p className="disabled-reason">{apiState === 'offline' ? 'Start the API to enable forecasts.' : 'Add data and train a model to enable forecasts.'}</p>}
              </form>
            </div>
            <div className="result-panel">
              <div className="panel-top result-top">
                <div>
                  <span className="eyebrow">{pipelineMode === 'live' ? 'REAL-TIME FORECAST WINDOW' : 'MODELED NEXT-DAY WINDOW'}</span>
                  <h2>{forecast ? new Date(`${forecast.forecast_for}T12:00:00`).toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'short' }) : 'Awaiting estimate'}</h2>
                </div>
                <span className="result-icon"><CloudSun size={20} /></span>
              </div>
              {forecast ? <div className="result-content">
                <div className="result-number">{forecast.forecast_aqi}<span>AQI</span></div>
                <div className="category-pill"><span />{forecast.category}</div>
                <p>{forecast.advisory}</p>
                <div className="validation-note">
                  <span>{pipelineMode === 'live' ? 'PIPELINE INPUT' : 'HOLDOUT ERROR REFERENCE'}</span>
                  <strong>{pipelineMode === 'live' ? 'Live 7-Day Telemetry' : (forecast.validation_mae == null ? 'Not available' : `${forecast.validation_mae} AQI points`)}</strong>
                  <small>{pipelineMode === 'live' ? 'Forecast derived from real-time 7-day ambient PM2.5 converted to Indian CPCB NAQI.' : 'Mean absolute error on the test year; this is not a guaranteed prediction range.'}</small>
                </div>
                <small>Estimated by {forecast.model} · {forecast.research_notice}</small>
              </div> : <div className="result-empty"><div className="air-lines"><span /><span /><span /></div><p>Your next-day estimate<br />will appear here.</p><small>No forecast has been generated</small></div>}
              <div className="result-footer"><span><span className="footer-dot" /> CPCB CATEGORY BANDS</span><span>0 — 500+</span></div>
            </div>
          </section>
          <section className="metrics-row"><Stat label="7-DAY MOVEMENT" value={history.length > 1 ? `${history.at(-1).aqi - history[Math.max(0, history.length - 7)].aqi > 0 ? '+' : ''}${(history.at(-1).aqi - history[Math.max(0, history.length - 7)].aqi).toFixed(0)}` : '—'} note="AQI points across the latest week" icon={Activity} /><Stat label="HOLDOUT MAE" value={forecast?.validation_mae != null ? `${forecast.validation_mae} pts` : '—'} note="Average error on unseen test data" icon={BarChart3} /><Stat label="CITIES IN DATA" value={cities.length || '—'} note="Available for city-level analysis" icon={GitCompareArrows} /><Stat label="MODEL BASELINE" value="Persistence" note="Tomorrow equals the latest AQI" icon={CloudSun} /></section>
          <section className="history-section"><div className="section-heading"><div><span className="eyebrow">OBSERVED SERIES</span><h2>{city} · AQI over time</h2></div><div className="history-tools"><div className="range-switch" aria-label="Chart time range">{[7, 30, 90].map((days) => <button key={days} type="button" className={rangeDays === days ? 'selected' : ''} onClick={() => setRangeDays(days)}>{days}D</button>)}</div><div className="chart-legend"><span className="legend-line" /> {city}<span className="legend-dash" /> {comparisonCity || 'Comparison'}</div></div></div><div className="chart-panel"><TrendChart points={history} comparisonPoints={compareHistory} comparisonName={comparisonCity} forecast={forecast?.forecast_aqi} rangeDays={rangeDays} /></div><div className="comparison-strip"><div><span className="eyebrow">COMPARE CITIES</span><strong>How does the pattern differ?</strong></div><label className="select-wrap compare-select"><span className="sr-only">Comparison city</span><select value={comparisonCity} onChange={(event) => setCompareCity(event.target.value)}>{cities.filter((name) => name.toLowerCase() !== city.toLowerCase()).map((name) => <option key={name}>{name}</option>)}</select><ChevronDown size={16} /></label><div className="compare-value"><small>{city} latest</small><strong>{history.at(-1)?.aqi ?? '—'}</strong></div><div className="compare-value"><small>{comparisonCity || 'Comparison'} latest</small><strong>{compareHistory.at(-1)?.aqi ?? '—'}</strong></div></div></section>
          <div className="footnote"><span>DATA NOTE</span><p>Live readings come from Open-Meteo in US AQI. The next-day estimate uses a separate XGBoost model trained on historical Indian AQI data and is not an official CPCB forecast or medical advice.</p></div>
        </>}

        {page === 'transfer' && <>
          <section className="page-heading compact-heading">
            <div>
              <div className="eyebrow green-eyebrow"><span className="tiny-line" /> CITY COMPARISON <span className="heading-separator">/</span> INDIA</div>
              <h1>Learn in one city. <span>Test in another.</span></h1>
              <p>See whether a model trained on one city’s past AQI also makes useful estimates for a different city.</p>
            </div>
          </section>

          <div className="pipeline-toggle-bar">
            <span className="toggle-label">TRANSFER EVALUATION:</span>
            <div className="toggle-buttons">
              <button
                type="button"
                className={`toggle-btn ${transferMode === 'live' ? 'toggle-active' : ''}`}
                onClick={() => setTransferMode('live')}
              >
                <Activity size={14} /> ⚡ Live Cross-City Transfer (Nov 2026)
              </button>
              <button
                type="button"
                className={`toggle-btn ${transferMode === 'matrix' ? 'toggle-active' : ''}`}
                onClick={() => setTransferMode('matrix')}
              >
                <BookOpen size={14} /> 📚 Historical Transfer Matrix (CPCB)
              </button>
            </div>
          </div>

          {error && <div className="alert"><CircleHelp size={17} /><span>{error}</span><button aria-label="Dismiss" onClick={() => setError('')}><X size={15} /></button></div>}

          {transferMode === 'live' ? (
            <section className="overview-grid" style={{ minHeight: 'auto', marginBottom: 28 }}>
              <div className="forecast-panel">
                <div className="panel-top">
                  <div>
                    <span className="eyebrow">ZERO-SHOT DOMAIN ADAPTATION</span>
                    <h2>Live transfer workbench</h2>
                  </div>
                  <span className="model-chip"><span /> {apiState === 'ready' ? 'MODEL READY' : 'MODEL UNAVAILABLE'}</span>
                </div>

                <div className="forecast-form">
                  <div className="field-block">
                    <label className="field-label" htmlFor="source-city-select">Source City (Trained Model Anchor)</label>
                    <div className="select-wrap">
                      <select id="source-city-select" value={transferSourceCity} onChange={(e) => setTransferSourceCity(e.target.value)}>
                        {(cities.length ? cities : CITY_CHOICES).map((name) => <option key={`src-${name}`}>{name}</option>)}
                      </select>
                      <ChevronDown size={16} />
                    </div>
                  </div>

                  <div className="field-block">
                    <label className="field-label" htmlFor="target-city-select">Target City (Live Telemetry Stream)</label>
                    <div className="select-wrap">
                      <select id="target-city-select" value={transferTargetCity} onChange={(e) => setTransferTargetCity(e.target.value)}>
                        {(cities.length ? cities : CITY_CHOICES).map((name) => <option key={`tgt-${name}`}>{name}</option>)}
                      </select>
                      <ChevronDown size={16} />
                    </div>
                  </div>

                  <p className="form-hint">
                    <CircleHelp size={14} /> Tests whether {transferSourceCity}'s trained model can predict {transferTargetCity}'s air quality using only {transferTargetCity}'s live Open-Meteo telemetry stream.
                  </p>

                  <button
                    className="primary-button"
                    type="button"
                    onClick={runLiveTransfer}
                    disabled={liveTransferBusy}
                  >
                    {liveTransferBusy ? <LoaderCircle className="spin" size={17} /> : <Activity size={17} />}
                    <span>{liveTransferBusy ? 'Running live transfer…' : `Transfer ${transferSourceCity} → ${transferTargetCity}`}</span>
                    <ArrowUpRight size={16} />
                  </button>
                  {liveTransferError && <p className="disabled-reason">{liveTransferError}</p>}
                </div>
              </div>

              <div className="result-panel">
                <div className="panel-top result-top">
                  <div>
                    <span className="eyebrow">CROSS-CITY PREDICTION</span>
                    <h2>{transferSourceCity} → {transferTargetCity}</h2>
                  </div>
                  <span className="result-icon"><GitCompareArrows size={20} /></span>
                </div>

                {liveTransferResult ? (
                  <div className="result-content">
                    <div className="result-number">
                      {liveTransferResult.transferred_forecast_aqi}
                      <span>AQI</span>
                    </div>
                    <div className="category-pill"><span />{liveTransferResult.transferred_category}</div>
                    <p>{liveTransferResult.advisory}</p>
                    <div className="validation-note">
                      <span>TARGET CITY LIVE STREAM</span>
                      <strong>{liveTransferResult.test_city} · {liveTransferResult.target_current_aqi} AQI ({liveTransferResult.target_current_pm25} µg/m³ PM2.5)</strong>
                      <small>Observed live on {liveTransferResult.target_observed_date}. Forecast computed without historical training data for {liveTransferResult.test_city}.</small>
                    </div>
                    {liveTransferResult.historical_rmse != null && (
                      <div className="validation-note" style={{ borderLeftColor: '#38bdf8' }}>
                        <span>HISTORICAL BENCHMARK RMSE</span>
                        <strong>{liveTransferResult.historical_rmse} AQI points</strong>
                        <small>Average holdout error achieved by {liveTransferResult.train_city} model when tested on historical {liveTransferResult.test_city} records.</small>
                      </div>
                    )}
                    <small>{liveTransferResult.research_insight}</small>
                  </div>
                ) : (
                  <div className="result-empty">
                    <div className="air-lines"><span /><span /><span /></div>
                    <p>Live transfer forecast<br />will appear here.</p>
                    <small>Click "Transfer {transferSourceCity} → {transferTargetCity}" to run</small>
                  </div>
                )}
                <div className="result-footer">
                  <span><span className="footer-dot" /> ZERO-SHOT CROSS-CITY INFERENCE</span>
                  <span>OPEN-METEO 2026</span>
                </div>
              </div>
            </section>
          ) : (
            <>
              <div className="experiment-strip">
                <span><Microscope size={17} /> HOW TO READ THIS</span>
                <p>Each row shows a city used for training. Each column shows a city used for testing. A lower RMSE means the estimate was closer to the real AQI. The diagonal compares the model on the same city it trained on.</p>
              </div>
              <section className="data-section">
                <div className="section-heading">
                  <div>
                    <span className="eyebrow">PREDICTION ERROR</span>
                    <h2>Training city compared with testing city</h2>
                  </div>
                  {matrix && <span className="dataset-tag">HELD-OUT YEAR · {matrix.test_year}</span>}
                </div>
                <div className="table-wrap">
                  {matrix?.results?.length ? (
                    <table className="matrix-table">
                      <thead>
                        <tr>
                          <th>TRAIN ↓ / TEST →</th>
                          {matrix.cities.map((name) => <th key={name}>{name}</th>)}
                        </tr>
                      </thead>
                      <tbody>
                        {matrix.cities.map((trainCity) => (
                          <tr key={trainCity}>
                            <th>{trainCity}</th>
                            {matrix.cities.map((testCity) => {
                              const result = matrix.results.find((item) => item.train_city === trainCity && item.test_city === testCity);
                              return (
                                <td key={testCity} className={trainCity === testCity ? 'self-cell' : ''}>
                                  {result ? result.rmse.toFixed(1) : '—'}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <EmptyState
                      icon={GitCompareArrows}
                      title="Transfer results appear after training data is added"
                      detail="The matrix is computed from real held-out observations; no sample values are shown."
                    />
                  )}
                </div>
                <p className="table-caption">Values are RMSE in AQI points: the smaller the number, the closer the prediction. Compare off-diagonal cells to judge how well the model travels to another city.</p>
              </section>
            </>
          )}

          <section className="metrics-row three-stats"><Stat label="TEST METHOD" value="Past → future" note="The model only uses earlier observations" icon={Activity} /><Stat label="CITY NAME" value="Not used" note="The model learns patterns, not labels" icon={GitCompareArrows} /><Stat label="SIMPLE BASELINE" value="Today → tomorrow" note="The latest value becomes the estimate" icon={Gauge} /></section>
        </>}

        {page === 'explain' && <><section className="page-heading compact-heading"><div><div className="eyebrow green-eyebrow"><span className="tiny-line" /> MODEL DETAILS <span className="heading-separator">/</span> INDIA</div><h1>What moves <span>the estimate?</span></h1><p>See which inputs the model uses most, without treating them as causes.</p></div><div className="select-wrap city-small"><select value={city} onChange={(event) => { setCity(event.target.value); setExplanation(null) }}>{(cities.length ? cities : CITY_CHOICES).map((name) => <option key={name}>{name}</option>)}</select><ChevronDown size={16} /></div></section>{error && <div className="alert"><CircleHelp size={17} /><span>{error}</span><button aria-label="Dismiss" onClick={() => setError('')}><X size={15} /></button></div>}<section className="data-section explain-section"><div className="section-heading"><div><span className="eyebrow">MOST USED INPUTS</span><h2>{city} · leading features</h2></div>{explanation && <span className="dataset-tag">{explanation.method.toUpperCase()}</span>}</div>{explanation?.features?.length ? <div className="importance-list">{explanation.features.map((feature, index) => <div className="importance-row" key={feature.feature}><span className="importance-rank">{String(index + 1).padStart(2, '0')}</span><span className="importance-name">{feature.feature.replaceAll('_', ' ')}</span><span className="importance-track"><span style={{ width: `${Math.max(3, feature.importance / explanation.features[0].importance * 100)}%` }} /></span><span className="importance-value">{feature.importance.toFixed(3)}</span></div>)}</div> : <EmptyState icon={BarChart3} title="Train a model to inspect feature importance" detail="The chart will use the fitted model's global importance scores; SHAP-based local explanations are a later research step." />}<div className="notice-line"><CircleHelp size={16} /><p>Importance describes how the fitted model uses features overall. It does not show that a feature causes AQI to change, and it may differ by city.</p></div></section></>}

        {page === 'method' && <><section className="page-heading compact-heading"><div><div className="eyebrow green-eyebrow"><span className="tiny-line" /> ABOUT THE PROJECT <span className="heading-separator">/</span> METHOD</div><h1>How the forecast <span>works.</span></h1><p>A next-day AQI model with a simple city-comparison view.</p></div></section><section className="method-grid"><article className="method-block"><span className="method-index">01</span><div><span className="eyebrow">QUESTION</span><h2>Can one city's history help forecast another?</h2><p>Train on data-rich Indian cities, test on a city the model has not seen, then measure how 30, 60, and 90 days of local data change error.</p></div></article><article className="method-block"><span className="method-index">02</span><div><span className="eyebrow">TARGET</span><h2>Next-day AQI, AQI(t + 1)</h2><p>Past AQI and PM2.5 lags, trailing statistics, available pollutants, weather, and cyclical calendar features. City identity is excluded from model inputs.</p></div></article><article className="method-block"><span className="method-index">03</span><div><span className="eyebrow">VALIDATION</span><h2>Time moves forward. Always.</h2><p>Chronological train and test splits protect the evaluation from future leakage. Every model is compared against persistence: tomorrow equals today.</p></div></article><article className="method-block"><span className="method-index">04</span><div><span className="eyebrow">EVIDENCE</span><h2>MAE · RMSE · R² · category scores</h2><p>Results remain blank until real data is loaded and the experiments are run. The two attached project guides propose different source periods; resolve this before final reporting.</p></div></article></section><section className="source-band"><span className="eyebrow">DATA SOURCES</span><h2>Three sources. Choose the study window.</h2><div className="source-options"><p><b><a href="https://www.kaggle.com/datasets/saikiranudayana/india-air-quality-index-aqi-dataset-20232025" target="_blank" rel="noreferrer">India AQI · 2023–2025 ↗</a></b><span>Recent AQI dataset. Confirm actual file coverage and licence before selecting it.</span></p><p><b><a href="https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india" target="_blank" rel="noreferrer">India Air Quality · CPCB/Kaggle ↗</a></b><span>Historical city-day data; the guide specifies 2015–2020. Ahmedabad is the Gujarat proxy, and the 2020 lockdown needs explicit treatment.</span></p><p><b><a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank" rel="noreferrer">Open-Meteo · Historical Weather ↗</a></b><span>Daily mean temperature, relative humidity, wind speed, precipitation, and surface pressure by coordinates. Check current API terms and coverage.</span></p></div><div className="source-note-inline"><Leaf size={16} /><span>Choose one primary AQI period. Record source version, licence, dates, city coverage, and weather merge details before reporting results.</span></div></section></>}
        <footer className="page-footer"><span>AIR / FIELD · INDIA AQI</span><span>ESTIMATE ONLY <span className="footer-sep">·</span> NOT AN OFFICIAL ADVISORY</span></footer>
      </div>
    </main>
  </div>
}

export default App
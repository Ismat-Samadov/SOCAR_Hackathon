import React, { useRef } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const data = [
  {
    name: 'GPT-4.1',
    Quality_Score: 52.00,
    Similarity: 0.00,
    Citation_Score: 80.00,
    Completeness: 100.0,
    Response_Time: 6.38
  },
  {
    name: 'Llama-4-Maverick',
    Quality_Score: 52.00,
    Similarity: 0.00,
    Citation_Score: 80.00,
    Completeness: 100.0,
    Response_Time: 4.00
  },
  {
    name: 'DeepSeek-R1',
    Quality_Score: 32.27,
    Similarity: 1.54,
    Citation_Score: 33.33,
    Completeness: 91.6,
    Response_Time: 10.98
  }
];

const modelColors = {
  'GPT-4.1': '#10b981',
  'Llama-4-Maverick': '#8b5cf6',
  'DeepSeek-R1': '#f59e0b'
};

const radarData = [
  { metric: 'Quality', 'GPT-4.1': 52, 'Llama-4-Maverick': 52, 'DeepSeek-R1': 32.27 },
  { metric: 'Citation', 'GPT-4.1': 80, 'Llama-4-Maverick': 80, 'DeepSeek-R1': 33.33 },
  { metric: 'Completeness', 'GPT-4.1': 100, 'Llama-4-Maverick': 100, 'DeepSeek-R1': 91.6 },
  { metric: 'Speed', 'GPT-4.1': 40, 'Llama-4-Maverick': 65, 'DeepSeek-R1': 10 }
];

export default function LLMBenchmarkCharts() {
  const chartRefs = {
    quality: useRef(null),
    metrics: useRef(null),
    radar: useRef(null),
    time: useRef(null)
  };

  const downloadChart = (chartName) => {
    const chartContainer = chartRefs[chartName].current;
    if (!chartContainer) return;
    
    const svg = chartContainer.querySelector('svg');
    if (!svg) return;
    
    const svgData = new XMLSerializer().serializeToString(svg);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `llm-benchmark-${chartName}-chart.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: 'none',
          borderRadius: '10px',
          padding: '14px 18px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.3)'
        }}>
          <p style={{ color: '#f8fafc', fontWeight: 600, marginBottom: '10px', fontSize: '14px' }}>{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color, margin: '5px 0', fontSize: '13px' }}>
              {entry.name}: <span style={{ fontWeight: 600 }}>{typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(160deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
      fontFamily: "'IBM Plex Sans', -apple-system, sans-serif",
      padding: '48px 24px'
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap');
        
        .chart-card {
          background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 20px;
          padding: 32px;
          margin-bottom: 32px;
          position: relative;
          backdrop-filter: blur(10px);
        }
        
        .chart-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 20px;
          right: 20px;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.5), rgba(16, 185, 129, 0.5), transparent);
        }
        
        .download-btn {
          position: absolute;
          top: 24px;
          right: 24px;
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(16, 185, 129, 0.2));
          color: #e2e8f0;
          border: 1px solid rgba(139, 92, 246, 0.3);
          padding: 10px 18px;
          border-radius: 10px;
          cursor: pointer;
          font-size: 13px;
          font-weight: 600;
          font-family: inherit;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: all 0.3s ease;
        }
        
        .download-btn:hover {
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.4), rgba(16, 185, 129, 0.4));
          border-color: rgba(139, 92, 246, 0.6);
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(139, 92, 246, 0.2);
        }
        
        .chart-title {
          font-size: 22px;
          font-weight: 700;
          color: #f1f5f9;
          margin: 0 0 8px 0;
          letter-spacing: -0.02em;
        }
        
        .chart-subtitle {
          font-size: 14px;
          color: #94a3b8;
          margin: 0 0 28px 0;
        }
        
        .model-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          border-radius: 30px;
          font-size: 13px;
          font-weight: 600;
          margin-right: 12px;
          margin-bottom: 12px;
        }
        
        .stat-card {
          background: rgba(30, 41, 59, 0.5);
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 12px;
          padding: 20px;
          text-align: center;
        }
        
        .stat-value {
          font-size: 32px;
          font-weight: 700;
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 12px;
          color: #94a3b8;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
      `}</style>

      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '56px' }}>
          <h1 style={{
            fontSize: '42px',
            fontWeight: 700,
            background: 'linear-gradient(135deg, #f1f5f9, #94a3b8)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: '0 0 16px 0',
            letterSpacing: '-0.03em'
          }}>
            LLM Benchmarking Results
          </h1>
          <p style={{
            fontSize: '17px',
            color: '#64748b',
            margin: '0 0 32px 0'
          }}>
            Performance comparison across leading language models
          </p>
          
          <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '12px' }}>
            {data.map((model) => (
              <div 
                key={model.name}
                className="model-badge"
                style={{ 
                  background: `${modelColors[model.name]}20`,
                  border: `1px solid ${modelColors[model.name]}40`,
                  color: modelColors[model.name]
                }}
              >
                <span style={{ 
                  width: '10px', 
                  height: '10px', 
                  borderRadius: '50%', 
                  background: modelColors[model.name],
                  boxShadow: `0 0 12px ${modelColors[model.name]}60`
                }}></span>
                {model.name}
              </div>
            ))}
          </div>
        </div>

        {/* Summary Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '32px' }}>
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#10b981' }}>52.0</div>
            <div className="stat-label">Best Quality Score</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#8b5cf6' }}>80.0</div>
            <div className="stat-label">Best Citation Score</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#3b82f6' }}>100%</div>
            <div className="stat-label">Max Completeness</div>
          </div>
          <div className="stat-card">
            <div className="stat-value" style={{ color: '#f59e0b' }}>4.00s</div>
            <div className="stat-label">Fastest Response</div>
          </div>
        </div>

        {/* Quality Score Bar Chart */}
        <div className="chart-card" ref={chartRefs.quality}>
          <button className="download-btn" onClick={() => downloadChart('quality')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
            </svg>
            Save SVG
          </button>
          <h2 className="chart-title">Quality Score Comparison</h2>
          <p className="chart-subtitle">Overall quality assessment (higher is better)</p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <defs>
                <linearGradient id="gpt4Gradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={1}/>
                  <stop offset="100%" stopColor="#10b981" stopOpacity={0.6}/>
                </linearGradient>
                <linearGradient id="llamaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8b5cf6" stopOpacity={1}/>
                  <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.6}/>
                </linearGradient>
                <linearGradient id="deepseekGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f59e0b" stopOpacity={1}/>
                  <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.6}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 13 }} axisLine={{ stroke: 'rgba(148, 163, 184, 0.2)' }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} domain={[0, 60]} />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="Quality_Score" 
                name="Quality Score"
                radius={[8, 8, 0, 0]}
                fill="#8b5cf6"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={modelColors[entry.name]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* All Metrics Grouped */}
        <div className="chart-card" ref={chartRefs.metrics}>
          <button className="download-btn" onClick={() => downloadChart('metrics')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
            </svg>
            Save SVG
          </button>
          <h2 className="chart-title">Full Metrics Breakdown</h2>
          <p className="chart-subtitle">Quality, Citation, and Completeness scores by model</p>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 13 }} axisLine={{ stroke: 'rgba(148, 163, 184, 0.2)' }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} domain={[0, 110]} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="Quality_Score" name="Quality" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Citation_Score" name="Citation" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Completeness" name="Completeness" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '32px' }}>
          {/* Radar Chart */}
          <div className="chart-card" ref={chartRefs.radar}>
            <button className="download-btn" onClick={() => downloadChart('radar')}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
              </svg>
              Save SVG
            </button>
            <h2 className="chart-title">Model Capability Profile</h2>
            <p className="chart-subtitle">Multi-dimensional performance comparison</p>
            <ResponsiveContainer width="100%" height={360}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(148, 163, 184, 0.2)" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
                <Radar name="GPT-4.1" dataKey="GPT-4.1" stroke="#10b981" fill="#10b981" fillOpacity={0.25} strokeWidth={2} />
                <Radar name="Llama-4-Maverick" dataKey="Llama-4-Maverick" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.2} strokeWidth={2} />
                <Radar name="DeepSeek-R1" dataKey="DeepSeek-R1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.15} strokeWidth={2} />
                <Legend />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Response Time Chart */}
          <div className="chart-card" ref={chartRefs.time}>
            <button className="download-btn" onClick={() => downloadChart('time')}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
              </svg>
              Save SVG
            </button>
            <h2 className="chart-title">Response Time Analysis</h2>
            <p className="chart-subtitle">Latency in seconds (lower is better)</p>
            <ResponsiveContainer width="100%" height={360}>
              <BarChart data={data} layout="vertical" margin={{ top: 20, right: 40, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" horizontal={true} vertical={false} />
                <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={{ stroke: 'rgba(148, 163, 184, 0.2)' }} domain={[0, 12]} />
                <YAxis dataKey="name" type="category" tick={{ fill: '#e2e8f0', fontSize: 13, fontWeight: 500 }} axisLine={false} tickLine={false} width={130} />
                <Tooltip content={<CustomTooltip />} />
                <Bar 
                  dataKey="Response_Time" 
                  name="Response Time (s)"
                  radius={[0, 8, 8, 0]}
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={modelColors[entry.name]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Data Table */}
        <div className="chart-card">
          <h2 className="chart-title">Complete Benchmark Data</h2>
          <p className="chart-subtitle">All metrics for each model</p>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid rgba(148, 163, 184, 0.2)' }}>
                  <th style={{ textAlign: 'left', padding: '14px 18px', fontWeight: 600, color: '#f1f5f9' }}>Model</th>
                  <th style={{ textAlign: 'right', padding: '14px 18px', fontWeight: 600, color: '#3b82f6' }}>Quality</th>
                  <th style={{ textAlign: 'right', padding: '14px 18px', fontWeight: 600, color: '#06b6d4' }}>Similarity</th>
                  <th style={{ textAlign: 'right', padding: '14px 18px', fontWeight: 600, color: '#10b981' }}>Citation</th>
                  <th style={{ textAlign: 'right', padding: '14px 18px', fontWeight: 600, color: '#8b5cf6' }}>Completeness</th>
                  <th style={{ textAlign: 'right', padding: '14px 18px', fontWeight: 600, color: '#f59e0b' }}>Time (s)</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(148, 163, 184, 0.1)' }}>
                    <td style={{ padding: '14px 18px', color: '#f1f5f9', fontWeight: 600 }}>
                      <span style={{ 
                        display: 'inline-block',
                        width: '8px', 
                        height: '8px', 
                        borderRadius: '50%', 
                        background: modelColors[row.name],
                        marginRight: '10px',
                        boxShadow: `0 0 8px ${modelColors[row.name]}60`
                      }}></span>
                      {row.name}
                    </td>
                    <td style={{ textAlign: 'right', padding: '14px 18px', color: '#3b82f6', fontWeight: 500 }}>{row.Quality_Score.toFixed(2)}</td>
                    <td style={{ textAlign: 'right', padding: '14px 18px', color: '#06b6d4' }}>{row.Similarity.toFixed(2)}</td>
                    <td style={{ textAlign: 'right', padding: '14px 18px', color: '#10b981' }}>{row.Citation_Score.toFixed(2)}</td>
                    <td style={{ textAlign: 'right', padding: '14px 18px', color: '#8b5cf6' }}>{row.Completeness.toFixed(1)}</td>
                    <td style={{ textAlign: 'right', padding: '14px 18px', color: '#f59e0b' }}>{row.Response_Time.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Key Insights */}
        <div className="chart-card" style={{ background: 'linear-gradient(145deg, rgba(16, 185, 129, 0.1), rgba(139, 92, 246, 0.1))' }}>
          <h2 className="chart-title">Key Insights</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginTop: '20px' }}>
            <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.5)', borderRadius: '12px', borderLeft: '3px solid #8b5cf6' }}>
              <h4 style={{ color: '#e2e8f0', margin: '0 0 8px 0', fontSize: '14px' }}>🏆 Speed Champion</h4>
              <p style={{ color: '#94a3b8', margin: 0, fontSize: '13px' }}>Llama-4-Maverick leads with 4.00s response time — 37% faster than GPT-4.1</p>
            </div>
            <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.5)', borderRadius: '12px', borderLeft: '3px solid #10b981' }}>
              <h4 style={{ color: '#e2e8f0', margin: '0 0 8px 0', fontSize: '14px' }}>📊 Quality Tie</h4>
              <p style={{ color: '#94a3b8', margin: 0, fontSize: '13px' }}>GPT-4.1 and Llama-4-Maverick tie at 52.0 quality score with identical citation performance</p>
            </div>
            <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.5)', borderRadius: '12px', borderLeft: '3px solid #f59e0b' }}>
              <h4 style={{ color: '#e2e8f0', margin: '0 0 8px 0', fontSize: '14px' }}>⚠️ DeepSeek Gap</h4>
              <p style={{ color: '#94a3b8', margin: 0, fontSize: '13px' }}>DeepSeek-R1 trails significantly with 32.27 quality and slowest response at 10.98s</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

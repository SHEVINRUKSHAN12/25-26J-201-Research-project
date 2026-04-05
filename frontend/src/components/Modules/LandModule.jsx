import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Download, Play } from 'lucide-react';
import './LandModule.css';

const API_BASE = 'http://127.0.0.1:8000/api/arcplan';

const initialConfig = {
    shape: 'rectangular',
    width: 20,
    height: 25,
    main_width: 12,
    main_depth: 15,
    extension_width: 8,
    extension_depth: 10,
    extension_side: 'right',
    bedrooms: 3,
    toilets: 2,
    kitchen: true,
    living: true,
    dining: true,
    carport: false,
    front: 'S'
};

const roomColors = {
    living: '#fff3e0',
    dining: '#fff9c4',
    kitchen: '#fff8e1',
    master_bedroom: '#e8f0fe',
    bedroom: '#ede7f6',
    toilet: '#e0f7fa',
    carport: '#e8eaf6'
};

export default function LandModule() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [config, setConfig] = useState(initialConfig);
    const [activeTab, setActiveTab] = useState('plot');
    const [status, setStatus] = useState('idle');
    const [progress, setProgress] = useState(0);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const plotRef = useRef(null);
    const planRef = useRef(null);

    const updateConfig = (patch) => setConfig((current) => ({ ...current, ...patch }));

    const runOptimize = async () => {
        setError('');
        setStatus('running');
        setProgress(20);
        try {
            const started = await fetch(`${API_BASE}/optimize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            }).then((res) => {
                if (!res.ok) throw new Error('Failed to start optimizer');
                return res.json();
            });
            setProgress(70);
            const optimized = await fetch(`${API_BASE}/result/${started.job_id}`).then((res) => {
                if (!res.ok) throw new Error('Failed to load optimizer result');
                return res.json();
            });
            setResult(optimized);
            setProgress(100);
            setStatus('done');
            setActiveTab('plan');
        } catch (err) {
            setError(err.message);
            setStatus('error');
        }
    };

    useEffect(() => {
        if (plotRef.current) drawLandPlot(plotRef.current, result, config);
        if (planRef.current) drawFloorPlan(planRef.current, result);
    }, [result, config, activeTab]);

    return (
        <div className="arc-shell">
            <div className="arc-topbar">
                <button className="arc-back" onClick={() => navigate(`/project/${id}`)}>
                    <ArrowLeft size={16} /> Back to Project
                </button>
                <div className="arc-brand"><span>HomeScope</span> / Land & Rules</div>
                <div className="arc-status"><span /> Backend Online</div>
            </div>

            <div className="arc-layout">
                <aside className="arc-sidebar">
                    <Section title="Land Shape">
                        <Segmented
                            options={[['rectangular', 'Rectangular'], ['lshape', 'L-Shape']]}
                            value={config.shape}
                            onChange={(shape) => updateConfig({ shape })}
                        />
                    </Section>

                    {config.shape === 'rectangular' ? (
                        <Section title="Dimensions">
                            <div className="arc-grid-2">
                                <NumberInput label="Width (m)" value={config.width} min={5} max={100} onChange={(width) => updateConfig({ width })} />
                                <NumberInput label="Depth (m)" value={config.height} min={5} max={100} onChange={(height) => updateConfig({ height })} />
                            </div>
                            <Area value={config.width * config.height} />
                        </Section>
                    ) : (
                        <Section title="L-Shape Zones">
                            <div className="arc-subtitle">Main Zone</div>
                            <div className="arc-grid-2">
                                <NumberInput label="Width (m)" value={config.main_width} min={5} max={50} onChange={(main_width) => updateConfig({ main_width })} />
                                <NumberInput label="Depth (m)" value={config.main_depth} min={5} max={50} onChange={(main_depth) => updateConfig({ main_depth })} />
                            </div>
                            <div className="arc-subtitle">Extension Zone</div>
                            <div className="arc-grid-2">
                                <NumberInput label="Width (m)" value={config.extension_width} min={3} max={30} onChange={(extension_width) => updateConfig({ extension_width })} />
                                <NumberInput label="Depth (m)" value={config.extension_depth} min={3} max={30} onChange={(extension_depth) => updateConfig({ extension_depth })} />
                            </div>
                            <Segmented
                                options={[['left', 'Left'], ['right', 'Right']]}
                                value={config.extension_side}
                                onChange={(extension_side) => updateConfig({ extension_side })}
                            />
                            <Area value={(config.main_width * config.main_depth) + (config.extension_width * config.extension_depth)} />
                        </Section>
                    )}

                    <Section title="Space Requirements">
                        <div className="arc-grid-2">
                            <Stepper label="Bedrooms" value={config.bedrooms} min={1} max={6} onChange={(bedrooms) => updateConfig({ bedrooms })} />
                            <Stepper label="Toilets" value={config.toilets} min={1} max={4} onChange={(toilets) => updateConfig({ toilets })} />
                        </div>
                        {['kitchen', 'living', 'dining', 'carport'].map((key) => (
                            <label className="arc-toggle-row" key={key}>
                                <span>{labelFor(key)}</span>
                                <input type="checkbox" checked={config[key]} onChange={(e) => updateConfig({ [key]: e.target.checked })} />
                            </label>
                        ))}
                    </Section>

                    <Section title="Front Orientation">
                        <Segmented
                            options={[['N', 'N'], ['S', 'S'], ['E', 'E'], ['W', 'W']]}
                            value={config.front}
                            onChange={(front) => updateConfig({ front })}
                            columns={4}
                        />
                    </Section>

                    <button className="arc-run" onClick={runOptimize} disabled={status === 'running'}>
                        <Play size={16} /> {status === 'running' ? 'Optimizing...' : 'Optimize Layout'}
                    </button>
                    {error && <div className="arc-error">{error}</div>}
                </aside>

                <main className="arc-main">
                    <header className="arc-work-header">
                        <div>
                            <h1>Integrated Land Optimizer</h1>
                            <p>AI-assisted layout generation with Sri Lankan setback rules.</p>
                        </div>
                        <div className="arc-score">
                            <span>Score</span>
                            <strong>{result?.score ?? '--'}</strong>
                        </div>
                    </header>

                    <div className="arc-tabs">
                        <button className={activeTab === 'plot' ? 'active' : ''} onClick={() => setActiveTab('plot')}>Land Plot</button>
                        <button className={activeTab === 'plan' ? 'active' : ''} onClick={() => setActiveTab('plan')}>Floor Plan</button>
                        <button className={activeTab === 'analysis' ? 'active' : ''} onClick={() => setActiveTab('analysis')}>Analysis</button>
                    </div>

                    <div className="arc-progress">
                        <div style={{ width: `${progress}%` }} />
                    </div>

                    {activeTab === 'plot' && (
                        <CanvasPanel canvasRef={plotRef} title="Land Plot" result={result} fallback="Run optimization to preview the buildable land plot." />
                    )}
                    {activeTab === 'plan' && (
                        <CanvasPanel canvasRef={planRef} title="Optimized Floor Plan" result={result} fallback="Run optimization to generate the floor plan." />
                    )}
                    {activeTab === 'analysis' && <Analysis result={result} config={config} />}
                </main>
            </div>
        </div>
    );
}

function Section({ title, children }) {
    return <section className="arc-section"><h2>{title}</h2>{children}</section>;
}

function Segmented({ options, value, onChange, columns = 2 }) {
    return (
        <div className="arc-segmented" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
            {options.map(([key, label]) => (
                <button key={key} className={value === key ? 'active' : ''} onClick={() => onChange(key)}>{label}</button>
            ))}
        </div>
    );
}

function NumberInput({ label, value, min, max, onChange }) {
    const invalid = value < min || value > max;
    return (
        <label className="arc-field">
            <span>{label}</span>
            <input
                className={invalid ? 'invalid' : ''}
                type="number"
                min={min}
                max={max}
                step="0.5"
                value={value}
                onChange={(e) => {
                    const next = Number.parseFloat(e.target.value);
                    if (!Number.isNaN(next)) onChange(Math.max(min, Math.min(max, next)));
                }}
            />
            {invalid && <small>Min: {min}m, Max: {max}m</small>}
        </label>
    );
}

function Stepper({ label, value, min, max, onChange }) {
    return (
        <div className="arc-stepper-wrap">
            <span>{label}</span>
            <div className="arc-stepper">
                <button onClick={() => onChange(Math.max(min, value - 1))}>-</button>
                <strong>{value}</strong>
                <button onClick={() => onChange(Math.min(max, value + 1))}>+</button>
            </div>
        </div>
    );
}

function Area({ value }) {
    return <div className="arc-area">Total Area: {value.toFixed(2)} m2</div>;
}

function CanvasPanel({ canvasRef, title, result, fallback }) {
    return (
        <section className="arc-panel">
            <div className="arc-panel-head">
                <h2>{title}</h2>
                {result && <button onClick={() => downloadCanvas(canvasRef.current)}><Download size={15} /> PNG</button>}
            </div>
            {!result && <div className="arc-empty">{fallback}</div>}
            <canvas ref={canvasRef} className={!result ? 'hidden' : ''} />
        </section>
    );
}

function Analysis({ result, config }) {
    if (!result) return <section className="arc-panel"><div className="arc-empty">Run optimization to view analysis.</div></section>;
    const landArea = config.shape === 'lshape'
        ? (config.main_width * config.main_depth) + (config.extension_width * config.extension_depth)
        : config.width * config.height;
    const buildable = result.buildable_zone.w * result.buildable_zone.h;
    return (
        <section className="arc-panel arc-analysis">
            <Metric label="Feasibility" value={result.feasible ? 'Feasible' : 'Limited'} />
            <Metric label="Land Area" value={`${landArea.toFixed(1)} m2`} />
            <Metric label="Buildable Area" value={`${buildable.toFixed(1)} m2`} />
            <Metric label="Rooms" value={result.rooms.length} />
        </section>
    );
}

function Metric({ label, value }) {
    return <div className="arc-metric"><span>{label}</span><strong>{value}</strong></div>;
}

function labelFor(key) {
    return ({ kitchen: 'Kitchen', living: 'Living Room', dining: 'Dining Room', carport: 'Carport' })[key] || key;
}

function downloadCanvas(canvas) {
    if (!canvas) return;
    const link = document.createElement('a');
    link.download = 'homescope-land-plan.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
}

function drawLandPlot(canvas, result, config) {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const isL = config.shape === 'lshape';
    const width = isL ? config.main_width + config.extension_width : config.width;
    const height = isL ? Math.max(config.main_depth, config.extension_depth) : config.height;
    const scale = Math.min(650 / width, 420 / height);
    canvas.width = Math.round(width * scale + 90);
    canvas.height = Math.round(height * scale + 90);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    const ox = 45, oy = 45;
    ctx.strokeStyle = '#0f172a';
    ctx.lineWidth = 2;

    if (isL) {
        const offset = config.extension_side === 'left' ? config.extension_width * scale : 0;
        ctx.fillStyle = '#f8fafc';
        if (config.extension_side === 'left') ctx.fillRect(ox, oy, config.extension_width * scale, config.extension_depth * scale);
        ctx.fillRect(ox + offset, oy, config.main_width * scale, config.main_depth * scale);
        if (config.extension_side === 'right') ctx.fillRect(ox + config.main_width * scale, oy, config.extension_width * scale, config.extension_depth * scale);
        ctx.strokeRect(ox + offset, oy, config.main_width * scale, config.main_depth * scale);
        ctx.strokeRect(config.extension_side === 'left' ? ox : ox + config.main_width * scale, oy, config.extension_width * scale, config.extension_depth * scale);
    } else {
        ctx.fillStyle = '#f8fafc';
        ctx.fillRect(ox, oy, config.width * scale, config.height * scale);
        ctx.strokeRect(ox, oy, config.width * scale, config.height * scale);
    }

    if (result?.buildable_zone) {
        const bz = result.buildable_zone;
        ctx.setLineDash([6, 4]);
        ctx.strokeStyle = '#059669';
        ctx.strokeRect(ox + bz.x * scale, oy + bz.y * scale, bz.w * scale, bz.h * scale);
        ctx.setLineDash([]);
        ctx.fillStyle = '#059669';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('BUILDABLE ZONE', ox + (bz.x + bz.w / 2) * scale, oy + (bz.y + bz.h / 2) * scale);
    }
}

function drawFloorPlan(canvas, result) {
    if (!canvas || !result) return;
    const ctx = canvas.getContext('2d');
    const zone = result.buildable_zone;
    const scale = Math.min(720 / zone.w, 460 / zone.h);
    canvas.width = Math.round(zone.w * scale + 80);
    canvas.height = Math.round(zone.h * scale + 80);
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const rooms = packRooms(result.rooms, zone.x, zone.y, zone.w, zone.h);
    const ox = 40, oy = 40;
    rooms.forEach((room) => {
        const x = ox + (room.x - zone.x) * scale;
        const y = oy + (room.y - zone.y) * scale;
        const w = room.w * scale;
        const h = room.h * scale;
        ctx.fillStyle = roomColors[room.type] || '#f8fafc';
        ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = '#111827';
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);
        ctx.fillStyle = '#111827';
        ctx.font = 'bold 11px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(room.name.toUpperCase(), x + w / 2, y + h / 2 - 4);
        ctx.font = '10px monospace';
        ctx.fillText(`${room.w.toFixed(1)} x ${room.h.toFixed(1)}m`, x + w / 2, y + h / 2 + 10);
    });
}

function packRooms(rooms, x, y, w, h) {
    const result = [];
    split(rooms, 0, rooms.length, x, y, w, h, true, result);
    return result;
}

function split(rooms, start, end, x, y, w, h, vertical, output) {
    if (end <= start) return;
    if (end - start === 1) {
        output.push({ ...rooms[start], x, y, w, h });
        return;
    }
    const mid = Math.ceil((start + end) / 2);
    const ratio = rooms.slice(start, mid).reduce((sum, room) => sum + room.area, 0) /
        rooms.slice(start, end).reduce((sum, room) => sum + room.area, 0);
    if (vertical) {
        const w1 = w * ratio;
        split(rooms, start, mid, x, y, w1, h, false, output);
        split(rooms, mid, end, x + w1, y, w - w1, h, false, output);
    } else {
        const h1 = h * ratio;
        split(rooms, start, mid, x, y, w, h1, true, output);
        split(rooms, mid, end, x, y + h1, w, h - h1, true, output);
    }
}

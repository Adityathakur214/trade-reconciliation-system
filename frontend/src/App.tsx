import { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { AlertCircle, CheckCircle, Clock, ShieldAlert, Upload, X } from 'lucide-react';

interface Case {
  id: number;
  client_id: string;
  isin: string | null;
  internal_qty: number;
  dp_qty: number;
  qty_delta: number;
  state: string;
  severity: string;
  evidence_status: string | null;
  cut_at: string;
}

export default function App() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);

  const internalFileRef = useRef<HTMLInputElement>(null);
  const dpFileRef = useRef<HTMLInputElement>(null);

  const fetchCases = () => {
    setLoading(true);
    axios.get('http://127.0.0.1:8000/cases')
      .then((res) => {
        setCases(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching cases:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    const internalFile = internalFileRef.current?.files?.[0];
    const dpFile = dpFileRef.current?.files?.[0];

    if (!internalFile || !dpFile) {
      alert("Dono files (Internal CSV aur DP HTML) select karna zaroori hai!");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("cut_at", new Date().toISOString());
    formData.append("internal_file", internalFile);
    formData.append("dp_file", dpFile);

    try {
      await axios.post('http://127.0.0.1:8000/imports/holdings', formData);
      setShowUpload(false);
      fetchCases(); // Table ko naye data ke sath refresh karein
    } catch (err) {
      console.error(err);
      alert("Upload fail ho gaya. Check karein ki backend (FastAPI) chal raha hai ya nahi.");
    } finally {
      setUploading(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-bold flex items-center gap-1 w-max"><ShieldAlert size={14}/> CRITICAL</span>;
      case 'HIGH': return <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded text-xs font-bold">HIGH</span>;
      case 'MEDIUM': return <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs font-bold">MEDIUM</span>;
      default: return <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-bold">LOW</span>;
    }
  };

  const getStateIcon = (state: string) => {
    switch (state) {
      case 'OPEN': return <AlertCircle size={16} className="text-orange-500" />;
      case 'RESOLVED': return <CheckCircle size={16} className="text-green-500" />;
      case 'NEEDS_SOURCE': return <Clock size={16} className="text-blue-500" />;
      default: return <Clock size={16} className="text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen p-8 font-sans text-slate-800 bg-slate-50 relative">
      
      {/* Upload Modal */}
      {showUpload && (
        <div className="absolute inset-0 bg-slate-900/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl w-96">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold">Upload Sync Sources</h2>
              <button onClick={() => setShowUpload(false)} className="text-slate-400 hover:text-slate-600"><X size={20}/></button>
            </div>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Internal Holdings (CSV)</label>
                <input type="file" accept=".csv" ref={internalFileRef} className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-slate-50 file:text-slate-700 hover:file:bg-slate-100 border border-slate-200 rounded-md"/>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">DP Positions (HTML)</label>
                <input type="file" accept=".html" ref={dpFileRef} className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-slate-50 file:text-slate-700 hover:file:bg-slate-100 border border-slate-200 rounded-md"/>
              </div>
              <button type="submit" disabled={uploading} className="w-full bg-slate-900 text-white py-2 rounded-md font-medium hover:bg-slate-800 disabled:opacity-50 flex items-center justify-center gap-2">
                {uploading ? "Processing..." : <><Upload size={16} /> Run Reconciliation</>}
              </button>
            </form>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Operations Exception Desk</h1>
            <p className="text-slate-500 mt-1">FDE Assessment - Read-only view for discrepancies</p>
          </div>
          <button 
            onClick={() => setShowUpload(true)}
            className="bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors shadow-sm flex items-center gap-2">
            <Upload size={16} /> Upload Sync Sources
          </button>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-100 border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500">
                  <th className="p-4 font-semibold">Case ID</th>
                  <th className="p-4 font-semibold">Client ID</th>
                  <th className="p-4 font-semibold">ISIN</th>
                  <th className="p-4 font-semibold text-right">Internal Qty</th>
                  <th className="p-4 font-semibold text-right">DP Qty</th>
                  <th className="p-4 font-semibold text-right">Delta</th>
                  <th className="p-4 font-semibold">Severity</th>
                  <th className="p-4 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr><td colSpan={8} className="p-8 text-center text-slate-500 font-medium">Loading cases from Backend...</td></tr>
                ) : cases.length === 0 ? (
                  <tr><td colSpan={8} className="p-8 text-center text-slate-500 font-medium">No cases found. Upload data to begin.</td></tr>
                ) : (
                  cases.map((c) => (
                    <tr key={c.id} className="hover:bg-slate-50 transition-colors">
                      <td className="p-4 font-medium text-slate-900">#{c.id}</td>
                      <td className="p-4 font-mono text-sm text-slate-600">{c.client_id}</td>
                      <td className="p-4 font-mono text-sm text-slate-600">{c.isin || 'N/A'}</td>
                      <td className="p-4 text-right tabular-nums">{c.internal_qty}</td>
                      <td className="p-4 text-right tabular-nums">{c.dp_qty}</td>
                      <td className={`p-4 text-right tabular-nums font-bold ${c.qty_delta !== 0 ? 'text-red-600' : 'text-slate-900'}`}>
                        {c.qty_delta}
                      </td>
                      <td className="p-4">{getSeverityBadge(c.severity)}</td>
                      <td className="p-4 flex items-center gap-2 text-sm font-medium">
                        {getStateIcon(c.state)}
                        {c.state}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
import React, { useState, useEffect } from 'react';
import { X, Siren, Droplet, Send, Hospital as HospitalIcon, Clock, AlertTriangle } from 'lucide-react';
import api from '../api/client';

const BLOOD_GROUPS = [
  'O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+',
  'Bombay (Oh)', 'Rh-null', 'Duffy Null Fy(a-b-)', 'Kell Null (K0)'
];

const URGENCIES = [
  { id: 'critical', label: 'CRITICAL (Immediate < 2 hrs)', badgeClass: 'bg-red-100 text-red-800 border-red-300 animate-pulse' },
  { id: 'high', label: 'HIGH (Within 6 hrs)', badgeClass: 'bg-rose-100 text-rose-800 border-rose-200' },
  { id: 'moderate', label: 'MODERATE (Within 24 hrs)', badgeClass: 'bg-stone-100 text-stone-700 border-stone-200' },
];

export default function EmergencySOSModal({ isOpen, onClose, onRequestCreated, currentUser }) {
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const [form, setForm] = useState({
    patient_name: '',
    blood_group: 'O-',
    hospital_id: '',
    units_required: 2,
    urgency_level: 'critical',
  });

  useEffect(() => {
    if (isOpen) {
      // Fetch verified hospitals for dropdown
      api.get('/hospitals/')
        .then((res) => {
          setHospitals(res.data);
          if (res.data.length > 0 && !form.hospital_id) {
            setForm((prev) => ({ ...prev, hospital_id: res.data[0].id }));
          }
        })
        .catch((err) => console.error('Failed to load hospitals:', err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    try {
      const res = await api.post('/blood-requests/', {
        hospital_id: form.hospital_id,
        patient_name: form.patient_name,
        blood_group: form.blood_group,
        units_required: Number(form.units_required),
        urgency_level: form.urgency_level,
      });

      onRequestCreated(res.data);
      onClose();
    } catch (err) {
      console.error('Request creation error:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to dispatch SOS alert. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 border border-rose-100 shadow-2xl relative animate-in fade-in zoom-in-95 duration-150 max-h-[90vh] overflow-y-auto">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-stone-400 hover:text-rose-600 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* SOS Header */}
        <div className="flex items-center gap-2 text-rose-600 mb-1">
          <Siren className="w-5 h-5 animate-bounce" />
          <span className="text-xs font-bold uppercase tracking-wider">Emergency Transfusion Requisition</span>
        </div>
        <h3 className="text-xl font-black text-stone-900 tracking-tight">Post Emergency SOS Broadcast</h3>
        <p className="text-xs text-stone-500 mb-4">
          Instantly triggers AWS SNS Transactional SMS and SES alert routing to nearby compatible donors.
        </p>

        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-xs font-semibold text-red-800">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          
          {/* Patient Details */}
          <div>
            <label className="block text-xs font-bold text-stone-700 mb-1">Patient Name / Hospital Case ID</label>
            <input
              type="text"
              required
              placeholder="e.g. Baby Maya Lin (Neonatal ICU)"
              value={form.patient_name}
              onChange={(e) => setForm({ ...form, patient_name: e.target.value })}
              className="w-full px-3.5 py-2 text-sm rounded-xl bg-white border border-rose-200 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none text-stone-800"
            />
          </div>

          {/* Blood Group Grid Badge Selector */}
          <div>
            <label className="block text-xs font-bold text-stone-700 mb-1.5 flex items-center justify-between">
              <span>Required Blood Group / Phenotype</span>
              <span className="text-[11px] text-rose-600 font-semibold">Select badge</span>
            </label>
            <div className="grid grid-cols-4 sm:grid-cols-6 gap-1.5">
              {BLOOD_GROUPS.map((bg) => {
                const isSelected = form.blood_group === bg;
                return (
                  <button
                    key={bg}
                    type="button"
                    onClick={() => setForm({ ...form, blood_group: bg })}
                    className={`py-2 px-1 rounded-xl text-xs font-extrabold transition text-center border ${
                      isSelected
                        ? 'bg-rose-600 text-white border-rose-600 shadow-sm shadow-rose-200 scale-[1.03]'
                        : 'bg-rose-50/50 text-rose-900 border-rose-100 hover:border-rose-300 hover:bg-rose-100/50'
                    }`}
                  >
                    {bg}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Hospital Selection & Units Required */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-stone-700 mb-1">Select Hospital</label>
              <select
                required
                value={form.hospital_id}
                onChange={(e) => setForm({ ...form, hospital_id: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-xl bg-white border border-rose-200 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none text-stone-800 font-semibold"
              >
                {hospitals.map((h) => (
                  <option key={h.id} value={h.id}>
                    {h.hospital_name} ({h.city})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-stone-700 mb-1">Units Required (Pints)</label>
              <input
                type="number"
                min="1"
                max="10"
                required
                value={form.units_required}
                onChange={(e) => setForm({ ...form, units_required: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-xl bg-white border border-rose-200 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none text-stone-800"
              />
            </div>
          </div>

          {/* Urgency Level Badges */}
          <div>
            <label className="block text-xs font-bold text-stone-700 mb-1.5">Urgency Level</label>
            <div className="grid grid-cols-3 gap-2">
              {URGENCIES.map((u) => {
                const isSelected = form.urgency_level === u.id;
                return (
                  <button
                    key={u.id}
                    type="button"
                    onClick={() => setForm({ ...form, urgency_level: u.id })}
                    className={`py-2 px-2 rounded-xl text-[11px] font-bold border transition text-center ${
                      isSelected
                        ? 'border-rose-500 bg-rose-50 text-rose-900 ring-2 ring-rose-400'
                        : 'border-rose-100 bg-white text-stone-600 hover:bg-rose-50/30'
                    }`}
                  >
                    {u.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Submit Action */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl font-bold text-sm text-white bg-rose-600 hover:bg-rose-700 shadow-sm shadow-rose-200 transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              <span>{loading ? 'Dispatching Cloud Broadcast...' : 'Broadcast SOS Request Now'}</span>
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}

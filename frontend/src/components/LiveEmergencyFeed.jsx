import React, { useState } from 'react';
import {
  Siren,
  Hospital as HospitalIcon,
  MapPin,
  Clock,
  HeartHandshake,
  CheckCircle2,
  Droplet,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import api from '../api/client';

export default function LiveEmergencyFeed({
  requests,
  onPledgeSuccess,
  currentUser,
  onOpenAuth
}) {
  const [pledgingId, setPledgingId] = useState(null);
  const [toastMsg, setToastMsg] = useState('');

  const handlePledge = async (requestId) => {
    if (!currentUser) {
      onOpenAuth();
      return;
    }

    setPledgingId(requestId);
    setToastMsg('');

    try {
      const res = await api.post('/donations/pledge', { request_id: requestId });
      setToastMsg('Pledge submitted successfully! The hospital has been notified.');
      onPledgeSuccess(requestId, res.data);
    } catch (err) {
      console.error('Pledge error:', err);
      const detail = err.response?.data?.detail || 'Failed to pledge. Verify donor profile setup.';
      setToastMsg(detail);
    } finally {
      setPledgingId(null);
      setTimeout(() => setToastMsg(''), 6000);
    }
  };

  const getUrgencyBadge = (urgency) => {
    switch (urgency?.toLowerCase()) {
      case 'critical':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-red-100 text-red-800 border border-red-200 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-red-600"></span>
            CRITICAL SOS
          </span>
        );
      case 'high':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
            HIGH URGENCY
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-stone-100 text-stone-700 border border-stone-200">
            MODERATE
          </span>
        );
    }
  };

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'fulfilled':
        return (
          <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
            ✓ Fulfilled
          </span>
        );
      case 'matched':
        return (
          <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
            Donor Matched
          </span>
        );
      default:
        return (
          <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
            Open Requisition
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Toast Alert */}
      {toastMsg && (
        <div className="p-4 rounded-xl bg-rose-100 border border-rose-300 text-rose-900 text-xs font-bold flex items-center justify-between shadow-sm animate-in fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-rose-600" />
            <span>{toastMsg}</span>
          </div>
          <button onClick={() => setToastMsg('')} className="text-rose-700 hover:text-rose-900 font-extrabold text-sm">
            ✕
          </button>
        </div>
      )}

      {/* Feed Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-rose-100 pb-4">
        <div>
          <h2 className="text-xl font-extrabold text-stone-900 flex items-center gap-2">
            <Siren className="w-5 h-5 text-rose-600" />
            Active Emergency Transfusion Feed
          </h2>
          <p className="text-xs text-stone-500 font-medium">
            Real-time broadcast feed requiring emergency donor matching across regional blood banks
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-bold text-stone-500">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
          <span>Live AWS SNS Stream Active</span>
        </div>
      </div>

      {/* Request Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {requests.map((req) => {
          const isFulfilled = req.status === 'fulfilled';
          const isMatched = req.status === 'matched';

          return (
            <div
              key={req.id}
              className="bg-white border border-rose-100 rounded-xl p-5 shadow-sm hover:border-rose-300 transition flex flex-col justify-between"
            >
              <div>
                {/* Header: Urgency & Status */}
                <div className="flex items-center justify-between mb-3">
                  {getUrgencyBadge(req.urgency_level)}
                  {getStatusBadge(req.status)}
                </div>

                {/* Patient & Blood Group */}
                <div className="flex items-start justify-between gap-3 mt-1">
                  <div>
                    <h3 className="font-extrabold text-stone-900 text-base leading-snug">
                      {req.patient_name}
                    </h3>
                    <p className="text-xs text-stone-500 font-medium flex items-center gap-1 mt-1">
                      <HospitalIcon className="w-3.5 h-3.5 text-rose-500" />
                      {req.hospital?.hospital_name || 'Emergency Regional Medical Center'}
                    </p>
                  </div>

                  <span className="text-xl font-black px-3 py-1 rounded-xl bg-rose-100 text-rose-800 border border-rose-200 shrink-0">
                    {req.blood_group}
                  </span>
                </div>

                {/* Location & Case Details */}
                <div className="mt-3.5 space-y-1.5 text-xs text-stone-600 bg-rose-50/30 p-3 rounded-xl border border-rose-100/70">
                  <p className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-rose-500" />
                    <span>{req.hospital?.city || 'Regional Center'}, {req.hospital?.address || 'Hospital Center'}</span>
                  </p>
                  <p className="flex items-center gap-1.5">
                    <Droplet className="w-3.5 h-3.5 text-rose-600" />
                    <span className="font-bold text-stone-800">{req.units_required} unit(s) required</span>
                  </p>
                  <p className="flex items-center gap-1.5 text-stone-400">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Posted {new Date(req.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </p>
                </div>

                <div className="mt-3 flex items-center gap-1.5 text-[11px] text-stone-500">
                  <ShieldCheck className="w-3.5 h-3.5 text-rose-600" />
                  <span>Verified Clinical Requisition Form</span>
                </div>
              </div>

              {/* Action: Pledge to Donate */}
              <div className="mt-5 pt-3.5 border-t border-rose-100 flex items-center justify-between">
                <span className="text-xs font-semibold text-stone-500">
                  {isFulfilled ? 'Transfusion Complete' : isMatched ? 'Matching in progress' : 'Awaiting Donor'}
                </span>

                {!isFulfilled && (
                  <button
                    onClick={() => handlePledge(req.id)}
                    disabled={pledgingId === req.id}
                    className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 shadow-sm shadow-rose-200 transition flex items-center gap-1.5 disabled:opacity-50"
                  >
                    <HeartHandshake className="w-3.5 h-3.5" />
                    <span>{pledgingId === req.id ? 'Pledging...' : 'Pledge to Donate'}</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}

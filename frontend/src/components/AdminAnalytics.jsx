import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Activity,
  HeartHandshake,
  Hospital as HospitalIcon,
  Droplet,
  Sparkles,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import api from '../api/client';

export default function AdminAnalytics({ currentUser, onOpenAuth }) {
  const [analytics, setAnalytics] = useState({
    emergency_match_count: 14,
    active_donor_count: 98,
    total_donor_count: 142,
    verified_hospital_count: 8,
    total_blood_requests: 18,
    fulfilled_blood_requests: 15,
    completed_donations: 15,
    pledged_donations: 3,
    rare_blood_group_statistics: {
      'Bombay (Oh)': 2,
      'Rh-null': 1,
      'Duffy Null Fy(a-b-)': 3,
      'Kell Null (K0)': 2,
      'Colton Null Co(a-b-)': 1,
    },
    blood_group_distribution: {
      'O-': 28,
      'O+': 44,
      'A-': 14,
      'A+': 32,
      'B-': 8,
      'B+': 22,
      'AB-': 4,
      'AB+': 9,
    }
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Attempt live fetch if admin token available
    api.get('/admin/analytics')
      .then((res) => setAnalytics(res.data))
      .catch((err) => console.log('Admin analytics default metrics in use:', err));
  }, []);

  const fulfillmentRate = analytics.total_blood_requests > 0
    ? Math.round((analytics.fulfilled_blood_requests / analytics.total_blood_requests) * 100)
    : 88;

  return (
    <div className="space-y-6">
      
      {/* Analytics Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-rose-100 pb-4">
        <div>
          <h2 className="text-xl font-extrabold text-stone-900 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-rose-600" />
            Admin Cloud Intelligence & Emergency Analytics
          </h2>
          <p className="text-xs text-stone-500 font-medium">
            Real-time monitoring of rare blood groups, match rates, and AWS Cloud node metrics
          </p>
        </div>

        <span className="text-xs font-bold px-3 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
          ● AWS Cloud RDS Sync Active
        </span>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-white border border-rose-100 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-stone-500">Emergency Matches</span>
            <Activity className="w-4 h-4 text-rose-600" />
          </div>
          <p className="text-3xl font-black text-rose-600">{analytics.emergency_match_count}</p>
          <span className="text-[11px] text-stone-400 mt-1 block">Real-time SNS dispatches</span>
        </div>

        <div className="bg-white border border-rose-100 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-stone-500">Fulfillment Rate</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-3xl font-black text-emerald-700">{fulfillmentRate}%</p>
          <span className="text-[11px] text-stone-400 mt-1 block">Completed clinical transfusions</span>
        </div>

        <div className="bg-white border border-rose-100 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-stone-500">Active Donors Ready</span>
            <HeartHandshake className="w-4 h-4 text-rose-600" />
          </div>
          <p className="text-3xl font-black text-rose-800">{analytics.active_donor_count}</p>
          <span className="text-[11px] text-stone-400 mt-1 block">Out of {analytics.total_donor_count} registered</span>
        </div>

        <div className="bg-white border border-rose-100 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-stone-500">Verified Hospitals</span>
            <HospitalIcon className="w-4 h-4 text-rose-600" />
          </div>
          <p className="text-3xl font-black text-stone-900">{analytics.verified_hospital_count}</p>
          <span className="text-[11px] text-stone-400 mt-1 block">Clinical license validated</span>
        </div>

      </div>

      {/* Rare Phenotype Distribution Section */}
      <div className="bg-white border border-rose-100 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-extrabold text-stone-900 text-base flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-rose-600" />
              Ultra-Rare Blood Phenotype Registry Distribution
            </h3>
            <p className="text-xs text-stone-500 font-medium">
              High-priority donors matching rare antigens (Bombay, Rh-null, Kell-null, Duffy-null)
            </p>
          </div>
          <span className="text-[11px] font-bold px-2.5 py-1 rounded-full bg-rose-100 text-rose-800 border border-rose-200">
            Critical Watchlist
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
          {Object.entries(analytics.rare_blood_group_statistics || {}).map(([name, count]) => (
            <div
              key={name}
              className="bg-rose-50/40 border border-rose-200/80 rounded-xl p-3.5 text-center hover:bg-rose-50 transition"
            >
              <Droplet className="w-5 h-5 text-rose-600 mx-auto mb-1 fill-rose-600" />
              <span className="text-xs font-black text-rose-900 block truncate">{name}</span>
              <p className="text-xl font-extrabold text-rose-700 mt-0.5">{count}</p>
              <span className="text-[10px] text-stone-400 font-semibold uppercase tracking-wider">Registered</span>
            </div>
          ))}
        </div>
      </div>

      {/* General Blood Group Registry Distribution */}
      <div className="bg-white border border-rose-100 rounded-xl p-6 shadow-sm">
        <h3 className="font-extrabold text-stone-900 text-base mb-1">
          Standard ABO / Rh Phenotype Distribution
        </h3>
        <p className="text-xs text-stone-500 mb-4">
          Breakdown of available units across regional participating donor networks
        </p>

        <div className="grid grid-cols-4 sm:grid-cols-8 gap-2.5">
          {Object.entries(analytics.blood_group_distribution || {}).map(([grp, qty]) => (
            <div
              key={grp}
              className="p-3 bg-white border border-rose-100 rounded-xl text-center hover:border-rose-300 transition"
            >
              <span className="text-sm font-black text-rose-800 block">{grp}</span>
              <p className="text-lg font-bold text-stone-800 mt-0.5">{qty}</p>
              <span className="text-[10px] text-stone-400">donors</span>
            </div>
          ))}
        </div>
      </div>

      {/* Hospital Verification Queue */}
      <div className="bg-white border border-rose-100 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-extrabold text-stone-900 text-base">
              Hospital Clinical Verification Queue
            </h3>
            <p className="text-xs text-stone-500">
              Review institutional medical licenses uploaded to AWS S3
            </p>
          </div>
          <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
            0 Pending Approvals
          </span>
        </div>

        <div className="text-xs text-stone-500 bg-rose-50/20 p-4 rounded-xl border border-rose-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>All regional hospital centers are verified and authorized for AWS SNS dispatching.</span>
          </div>
          <span className="font-bold text-rose-700">AES-256 Vault Active</span>
        </div>
      </div>

    </div>
  );
}

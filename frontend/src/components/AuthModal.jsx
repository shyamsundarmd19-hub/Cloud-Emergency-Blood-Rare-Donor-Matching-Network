import React, { useState } from 'react';
import { X, Droplet, User, Lock, Mail, Phone, ShieldCheck, HeartHandshake, Hospital } from 'lucide-react';
import api from '../api/client';

const ROLES = [
  { id: 'donor', label: 'Blood Donor', icon: HeartHandshake, desc: 'Pledge & save lives' },
  { id: 'patient', label: 'Patient / Family', icon: User, desc: 'Request urgent blood' },
  { id: 'hospital', label: 'Hospital Authority', icon: Hospital, desc: 'Manage clinical blood needs' },
  { id: 'admin', label: 'System Admin', icon: ShieldCheck, desc: 'Network oversight' },
];

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [role, setRole] = useState('donor');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
  });

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    try {
      if (isRegister) {
        // Register API
        await api.post('/auth/register', {
          name: form.name,
          email: form.email,
          phone: form.phone,
          role: role,
          password: form.password,
        });
      }

      // Login to obtain JWT
      const loginRes = await api.post('/auth/login', {
        email: form.email,
        password: form.password,
      });

      const { access_token, role: userRole, user_id, name } = loginRes.data;
      const userData = { id: user_id, name: name || form.name, email: form.email, role: userRole };

      localStorage.setItem('lifeline_token', access_token);
      localStorage.setItem('lifeline_user', JSON.stringify(userData));

      onAuthSuccess(userData);
      onClose();
    } catch (err) {
      console.error('Authentication error:', err);
      setErrorMsg(err.response?.data?.detail || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  // Quick switch for demo testing accounts
  const fillDemoAccount = (demoEmail, demoPass) => {
    setForm({
      ...form,
      email: demoEmail,
      password: demoPass,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 border border-rose-100 shadow-2xl relative animate-in fade-in zoom-in-95 duration-150">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-stone-400 hover:text-rose-600 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header Icon */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600">
            <Droplet className="w-5 h-5 fill-rose-600" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-stone-900">
              {isRegister ? 'Join LifeLine Network' : 'Access Your Account'}
            </h3>
            <p className="text-xs text-stone-500 font-medium">
              {isRegister ? 'Register as a donor, hospital or patient' : 'Secure JWT sign in for emergency dispatch'}
            </p>
          </div>
        </div>

        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-xs font-semibold text-red-800">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          {/* Role Selector (visible in Register mode) */}
          {isRegister && (
            <div>
              <label className="block text-xs font-bold text-stone-700 mb-1.5">Select Account Role</label>
              <div className="grid grid-cols-2 gap-2">
                {ROLES.map((r) => {
                  const Icon = r.icon;
                  const isSelected = role === r.id;
                  return (
                    <button
                      key={r.id}
                      type="button"
                      onClick={() => setRole(r.id)}
                      className={`p-2.5 rounded-xl border text-left transition flex flex-col justify-between ${
                        isSelected
                          ? 'border-rose-500 bg-rose-50/60 text-rose-900'
                          : 'border-rose-100 bg-white hover:bg-rose-50/30 text-stone-600'
                      }`}
                    >
                      <div className="flex items-center gap-1.5 mb-1">
                        <Icon className={`w-4 h-4 ${isSelected ? 'text-rose-600' : 'text-stone-400'}`} />
                        <span className="text-xs font-bold">{r.label}</span>
                      </div>
                      <span className="text-[10px] text-stone-500">{r.desc}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {isRegister && (
            <div>
              <label className="block text-xs font-semibold text-stone-700 mb-1">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 text-stone-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  required
                  placeholder="e.g. Dr. Maya Lin"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full pl-9 pr-3.5 py-2 text-sm rounded-xl bg-white border border-rose-200 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none text-stone-800"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-stone-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-stone-400 absolute left-3 top-2.5" />
              <input
                type="email"
                required
                placeholder="user@lifeline.org"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full pl-9 pr-3.5 py-2 text-sm rounded-xl bg-white border border-rose-200 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none text-stone-800"
              />
            </div>
          </div>

          {isRegister && (
            <div>
              <label className="block text-xs font-semibold text-stone-700 mb-1">Phone Number (SMS alerts)</label>
              <div className="relative">
                <Phone className="w-4 h-4 text-stone-400 absolute left-3 top-2.5" />
                <input
                  type="tel"
                  required
                  placeholder="+1 (555) 000-0000"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  className="w-full pl-9 pr-3.5 py-2 text-sm rounded-xl bg-white border border-rose-200 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none text-stone-800"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-stone-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-stone-400 absolute left-3 top-2.5" />
              <input
                type="password"
                required
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full pl-9 pr-3.5 py-2 text-sm rounded-xl bg-white border border-rose-200 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none text-stone-800"
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-xl font-bold text-sm text-white bg-rose-600 hover:bg-rose-700 shadow-sm shadow-rose-200 transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? 'Processing...' : isRegister ? 'Complete Registration' : 'Sign In to LifeLine'}
            </button>
          </div>

          {/* Mode Switcher */}
          <div className="text-center pt-2">
            <button
              type="button"
              onClick={() => {
                setIsRegister(!isRegister);
                setErrorMsg('');
              }}
              className="text-xs text-rose-600 hover:text-rose-700 font-semibold transition"
            >
              {isRegister ? 'Already registered? Click here to sign in' : "Don't have an account? Create one"}
            </button>
          </div>

          {/* Quick Demo Fill Buttons */}
          {!isRegister && (
            <div className="mt-4 pt-3 border-t border-rose-100 text-[11px] text-stone-500">
              <span className="font-semibold block mb-1.5 text-stone-700">Quick Test Credentials:</span>
              <div className="flex flex-wrap gap-1.5">
                <button
                  type="button"
                  onClick={() => fillDemoAccount('admin@lifeline.org', 'AdminPass2026!')}
                  className="px-2 py-1 rounded bg-rose-50 hover:bg-rose-100 text-rose-800 font-medium"
                >
                  Admin
                </button>
                <button
                  type="button"
                  onClick={() => fillDemoAccount('elena.vance@lifeline.org', 'DonorPass2026!')}
                  className="px-2 py-1 rounded bg-rose-50 hover:bg-rose-100 text-rose-800 font-medium"
                >
                  Donor (Bombay Oh)
                </button>
                <button
                  type="button"
                  onClick={() => fillDemoAccount('admin@stanfordhealth.org', 'HospitalPass2026!')}
                  className="px-2 py-1 rounded bg-rose-50 hover:bg-rose-100 text-rose-800 font-medium"
                >
                  Hospital Admin
                </button>
              </div>
            </div>
          )}
        </form>

      </div>
    </div>
  );
}

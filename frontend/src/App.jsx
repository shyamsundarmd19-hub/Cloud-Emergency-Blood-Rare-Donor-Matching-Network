import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AuthModal from './components/AuthModal';
import EmergencySOSModal from './components/EmergencySOSModal';
import LiveEmergencyFeed from './components/LiveEmergencyFeed';
import DonorDirectory from './components/DonorDirectory';
import DonorPanel from './components/DonorPanel';
import HospitalPanel from './components/HospitalPanel';
import AdminAnalytics from './components/AdminAnalytics';
import api from './api/client';
import {
  Droplet,
  Siren,
  HeartHandshake,
  ShieldCheck,
  Server,
  Cloud,
  Database,
  CheckCircle2,
  Sparkles,
  Zap,
  Activity
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('feed');
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isSOSOpen, setIsSOSOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [toastNotification, setToastNotification] = useState(null);

  // Initial Sample Requests adhering to schema
  const [requests, setRequests] = useState([
    {
      id: 'req-001',
      patient_name: 'Baby Maya Lin (Neonatal ICU)',
      blood_group: 'Bombay (Oh)',
      units_required: 2,
      urgency_level: 'critical',
      status: 'matched',
      created_at: new Date().toISOString(),
      hospital: {
        hospital_name: 'Stanford Hospital & Trauma Center',
        city: 'Palo Alto',
        address: '300 Pasteur Dr'
      }
    },
    {
      id: 'req-002',
      patient_name: 'James Wilson (Cardiothoracic Trauma)',
      blood_group: 'Rh-null',
      units_required: 1,
      urgency_level: 'critical',
      status: 'open',
      created_at: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
      hospital: {
        hospital_name: 'Mount Sinai Medical Center',
        city: 'New York',
        address: '1468 Madison Ave'
      }
    },
    {
      id: 'req-003',
      patient_name: 'Clara Jenkins (Emergency Obstetrics)',
      blood_group: 'O-',
      units_required: 3,
      urgency_level: 'high',
      status: 'open',
      created_at: new Date(Date.now() - 1000 * 60 * 75).toISOString(),
      hospital: {
        hospital_name: 'Stanford Hospital & Trauma Center',
        city: 'Palo Alto',
        address: '300 Pasteur Dr'
      }
    }
  ]);

  // Initial Donors
  const [donors, setDonors] = useState([
    {
      id: 'don-001',
      name: 'Dr. Elena Vance',
      blood_group: 'Bombay (Oh)',
      age: 32,
      gender: 'Female',
      city: 'Palo Alto',
      is_available: true,
      last_donated_date: '2026-04-15',
      user: { name: 'Dr. Elena Vance', phone: '+1 (415) 555-2671' }
    },
    {
      id: 'don-002',
      name: 'Marcus Aurelius Thorne',
      blood_group: 'Rh-null',
      age: 38,
      gender: 'Male',
      city: 'New York',
      is_available: true,
      last_donated_date: '2026-01-10',
      user: { name: 'Marcus Aurelius Thorne', phone: '+1 (212) 555-9812' }
    },
    {
      id: 'don-003',
      name: 'Sarah Connor',
      blood_group: 'O-',
      age: 29,
      gender: 'Female',
      city: 'Chicago',
      is_available: true,
      last_donated_date: '2026-06-20',
      user: { name: 'Sarah Connor', phone: '+1 (312) 555-3311' }
    },
    {
      id: 'don-004',
      name: 'Rajesh Sharma',
      blood_group: 'Kell Null (K0)',
      age: 41,
      gender: 'Male',
      city: 'Austin',
      is_available: true,
      last_donated_date: null,
      user: { name: 'Rajesh Sharma', phone: '+1 (512) 555-8900' }
    },
    {
      id: 'don-005',
      name: 'Clara Oswald',
      blood_group: 'Duffy Null Fy(a-b-)',
      age: 27,
      gender: 'Female',
      city: 'Palo Alto',
      is_available: true,
      last_donated_date: '2026-03-05',
      user: { name: 'Clara Oswald', phone: '+1 (206) 555-4422' }
    },
    {
      id: 'don-006',
      name: 'David Kim',
      blood_group: 'B+',
      age: 34,
      gender: 'Male',
      city: 'Boston',
      is_available: true,
      last_donated_date: '2026-07-01',
      user: { name: 'David Kim', phone: '+1 (617) 555-7788' }
    }
  ]);

  // Load user session and live data on startup
  useEffect(() => {
    const savedUser = localStorage.getItem('lifeline_user');
    if (savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem('lifeline_user');
      }
    }

    // Attempt live fetch from backend
    api.get('/blood-requests/')
      .then((res) => {
        if (res.data && res.data.length > 0) {
          setRequests(res.data);
        }
      })
      .catch((err) => console.log('Offline/Mock requests active:', err));

    api.get('/donors/?available_only=false')
      .then((res) => {
        if (res.data && res.data.length > 0) {
          setDonors(res.data);
        }
      })
      .catch((err) => console.log('Offline/Mock donors active:', err));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('lifeline_token');
    localStorage.removeItem('lifeline_user');
    setCurrentUser(null);
    setToastNotification('Signed out from LifeLine session.');
    setTimeout(() => setToastNotification(null), 4000);
  };

  const handleRequestCreated = (createdResponse) => {
    const newReq = createdResponse.blood_request || createdResponse;
    setRequests((prev) => [newReq, ...prev]);

    const summary = createdResponse.notification_summary;
    const recipientCount = summary?.matched_recipients || 1;
    setToastNotification(
      `🚨 SOS Broadcast Created! AWS SNS & SES alerts triggered to ${recipientCount} matching donor(s).`
    );
    setTimeout(() => setToastNotification(null), 8000);
    setActiveTab('feed');
  };

  const handlePledgeSuccess = (requestId, donationData) => {
    setRequests((prev) =>
      prev.map((r) => (r.id === requestId ? { ...r, status: 'matched' } : r))
    );
    setToastNotification(
      `Pledge confirmed for request #${requestId.slice(0, 8)}! Hospital notified.`
    );
    setTimeout(() => setToastNotification(null), 6000);
  };

  return (
    <div className="min-h-screen bg-red-50/40 text-stone-800 flex flex-col font-sans selection:bg-rose-200 selection:text-rose-900">
      
      {/* Toast Notification Alert */}
      {toastNotification && (
        <div className="fixed top-24 right-4 z-50 bg-rose-600 text-white px-5 py-3 rounded-xl shadow-lg border border-rose-500 flex items-center gap-3 animate-bounce">
          <Zap className="w-5 h-5 text-rose-200 shrink-0" />
          <span className="text-xs font-bold">{toastNotification}</span>
          <button
            onClick={() => setToastNotification(null)}
            className="ml-2 hover:opacity-75 text-white font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Header / Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentUser={currentUser}
        onOpenAuth={() => setIsAuthOpen(true)}
        onOpenSOS={() => setIsSOSOpen(true)}
        onLogout={handleLogout}
      />

      {/* Hero Quick Banner */}
      <section className="bg-white border-b border-rose-100 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200 text-[11px] font-bold mb-1.5">
              <Sparkles className="w-3.5 h-3.5 text-rose-600" />
              AWS Cloud Emergency Dispatch Network • Free Tier Architecture
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-stone-900 tracking-tight">
              Rapid Blood & Ultra-Rare Donor Matching
            </h1>
            <p className="text-xs text-stone-500 font-medium mt-1">
              Automated SNS transactional SMS alerting and S3 SSE-S3 encrypted medical clearance for critical transfusions.
            </p>
          </div>

          {/* Quick Metrics Bar */}
          <div className="flex items-center gap-3">
            <div className="px-3.5 py-2 rounded-xl bg-rose-50/60 border border-rose-100 text-center">
              <span className="text-[10px] font-semibold text-stone-500 block">Active SOS</span>
              <span className="text-base font-black text-rose-600">
                {requests.filter((r) => r.status === 'open').length}
              </span>
            </div>
            <div className="px-3.5 py-2 rounded-xl bg-rose-50/60 border border-rose-100 text-center">
              <span className="text-[10px] font-semibold text-stone-500 block">Matched</span>
              <span className="text-base font-black text-stone-800">
                {requests.filter((r) => r.status === 'matched').length}
              </span>
            </div>
            <div className="px-3.5 py-2 rounded-xl bg-rose-50/60 border border-rose-100 text-center">
              <span className="text-[10px] font-semibold text-stone-500 block">Rare Donors</span>
              <span className="text-base font-black text-rose-700">4</span>
            </div>
          </div>
        </div>
      </section>

      {/* Main View Area */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {activeTab === 'feed' && (
          <LiveEmergencyFeed
            requests={requests}
            onPledgeSuccess={handlePledgeSuccess}
            currentUser={currentUser}
            onOpenAuth={() => setIsAuthOpen(true)}
          />
        )}

        {activeTab === 'donors' && (
          <DonorDirectory donors={donors} />
        )}

        {activeTab === 'donor-portal' && (
          <DonorPanel
            currentUser={currentUser}
            onOpenAuth={() => setIsAuthOpen(true)}
          />
        )}

        {activeTab === 'hospitals' && (
          <HospitalPanel
            currentUser={currentUser}
            onOpenSOS={() => setIsSOSOpen(true)}
            onOpenAuth={() => setIsAuthOpen(true)}
          />
        )}

        {activeTab === 'admin' && (
          <AdminAnalytics
            currentUser={currentUser}
            onOpenAuth={() => setIsAuthOpen(true)}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-rose-100 py-6 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-stone-500 font-medium">
          <div className="flex items-center gap-2">
            <Droplet className="w-4 h-4 text-rose-600 fill-rose-600" />
            <strong className="text-stone-800">LifeLine</strong>
            <span>• Emergency Blood & Rare Donor Matching Network</span>
          </div>

          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 border border-rose-100">
              <Server className="w-3 h-3 text-rose-600" /> EC2 t2.micro
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 border border-rose-100">
              <Database className="w-3 h-3 text-rose-600" /> RDS PostgreSQL
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 border border-rose-100">
              <Cloud className="w-3 h-3 text-rose-600" /> S3 SSE-S3 AES256
            </span>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={(user) => {
          setCurrentUser(user);
          setToastNotification(`Welcome back, ${user.name}! Authenticated as ${user.role}.`);
          setTimeout(() => setToastNotification(null), 5000);
        }}
      />

      <EmergencySOSModal
        isOpen={isSOSOpen}
        onClose={() => setIsSOSOpen(false)}
        onRequestCreated={handleRequestCreated}
        currentUser={currentUser}
      />

    </div>
  );
}

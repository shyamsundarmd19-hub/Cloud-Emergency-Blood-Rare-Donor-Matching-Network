import React from 'react';
import {
  Droplet,
  Siren,
  HeartHandshake,
  Hospital,
  ShieldCheck,
  Activity,
  LogOut,
  User,
  PlusCircle
} from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  currentUser,
  onOpenAuth,
  onOpenSOS,
  onLogout
}) {
  return (
    <header className="sticky top-0 z-40 bg-white border-b border-red-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand Logo & Tagline */}
        <div 
          onClick={() => setActiveTab('feed')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-rose-500 to-rose-700 flex items-center justify-center text-white shadow-rose">
            <Droplet className="w-6 h-6 fill-white text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-2xl tracking-tight text-rose-600">LifeLine</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 border border-rose-200 uppercase tracking-wider">
                Emergency Network
              </span>
            </div>
            <p className="text-xs text-stone-500 font-medium">Cloud Blood & Rare Donor Matching</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1.5 bg-rose-50/50 p-1 rounded-2xl border border-rose-100">
          <button
            onClick={() => setActiveTab('feed')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === 'feed'
                ? 'bg-white text-rose-600 shadow-sm border border-rose-100'
                : 'text-stone-600 hover:text-rose-600 hover:bg-rose-100/50'
            }`}
          >
            <Siren className="w-4 h-4 text-rose-600" />
            Emergency Feed
          </button>

          <button
            onClick={() => setActiveTab('donors')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === 'donors'
                ? 'bg-white text-rose-600 shadow-sm border border-rose-100'
                : 'text-stone-600 hover:text-rose-600 hover:bg-rose-100/50'
            }`}
          >
            <HeartHandshake className="w-4 h-4 text-rose-600" />
            Find Donors
          </button>

          <button
            onClick={() => setActiveTab('donor-portal')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === 'donor-portal'
                ? 'bg-white text-rose-600 shadow-sm border border-rose-100'
                : 'text-stone-600 hover:text-rose-600 hover:bg-rose-100/50'
            }`}
          >
            <Activity className="w-4 h-4 text-rose-600" />
            Donor Portal
          </button>

          <button
            onClick={() => setActiveTab('hospitals')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === 'hospitals'
                ? 'bg-white text-rose-600 shadow-sm border border-rose-100'
                : 'text-stone-600 hover:text-rose-600 hover:bg-rose-100/50'
            }`}
          >
            <Hospital className="w-4 h-4 text-rose-600" />
            Hospitals
          </button>

          <button
            onClick={() => setActiveTab('admin')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === 'admin'
                ? 'bg-white text-rose-600 shadow-sm border border-rose-100'
                : 'text-stone-600 hover:text-rose-600 hover:bg-rose-100/50'
            }`}
          >
            <ShieldCheck className="w-4 h-4 text-rose-600" />
            Admin Analytics
          </button>
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenSOS}
            className="px-4 py-2.5 rounded-xl text-sm font-bold bg-rose-600 hover:bg-rose-700 text-white shadow-sm shadow-rose-200 transition flex items-center gap-2"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Post SOS Request</span>
          </button>

          {currentUser ? (
            <div className="flex items-center gap-2 pl-2 border-l border-red-100">
              <div className="hidden lg:block text-right">
                <p className="text-xs font-bold text-stone-800 leading-tight">{currentUser.name}</p>
                <span className="text-[10px] font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-100 capitalize">
                  {currentUser.role}
                </span>
              </div>
              <button
                onClick={onLogout}
                title="Logout"
                className="p-2.5 rounded-xl text-stone-500 hover:text-rose-600 hover:bg-rose-50 transition border border-rose-100"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="px-4 py-2.5 rounded-xl text-sm font-semibold bg-white border border-rose-200 text-rose-700 hover:bg-rose-50 transition flex items-center gap-2"
            >
              <User className="w-4 h-4 text-rose-600" />
              <span>Sign In</span>
            </button>
          )}
        </div>

      </div>
    </header>
  );
}

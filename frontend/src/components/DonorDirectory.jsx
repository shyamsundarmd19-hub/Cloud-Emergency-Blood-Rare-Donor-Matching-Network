import React, { useState } from 'react';
import { Search, HeartHandshake, MapPin, Phone, Droplet, Sparkles, UserCheck } from 'lucide-react';

const BLOOD_GROUPS = [
  'All', 'O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+',
  'Bombay (Oh)', 'Rh-null', 'Duffy Null Fy(a-b-)', 'Kell Null (K0)'
];

export default function DonorDirectory({ donors }) {
  const [selectedGroup, setSelectedGroup] = useState('All');
  const [cityFilter, setCityFilter] = useState('');
  const [onlyAvailable, setOnlyAvailable] = useState(true);

  const filtered = donors.filter((d) => {
    const matchesGroup = selectedGroup === 'All' || d.blood_group.toLowerCase().includes(selectedGroup.toLowerCase());
    const matchesCity = cityFilter === '' || d.city.toLowerCase().includes(cityFilter.toLowerCase());
    const matchesAvail = !onlyAvailable || d.is_available;
    return matchesGroup && matchesCity && matchesAvail;
  });

  return (
    <div className="space-y-6">
      
      {/* Directory Header */}
      <div className="border-b border-rose-100 pb-4">
        <h2 className="text-xl font-extrabold text-stone-900 flex items-center gap-2">
          <HeartHandshake className="w-5 h-5 text-rose-600" />
          Verified Blood & Rare Phenotype Donor Directory
        </h2>
        <p className="text-xs text-stone-500 font-medium">
          Direct registry of voluntary blood donors ready for regional emergency matching
        </p>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white border border-rose-100 rounded-xl p-4 shadow-sm space-y-3">
        
        {/* Blood Groups Selector */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
          {BLOOD_GROUPS.map((bg) => {
            const isSelected = selectedGroup === bg;
            return (
              <button
                key={bg}
                onClick={() => setSelectedGroup(bg)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition border ${
                  isSelected
                    ? 'bg-rose-600 text-white border-rose-600 shadow-sm shadow-rose-200'
                    : 'bg-rose-50/50 text-stone-700 border-rose-100 hover:bg-rose-100/50'
                }`}
              >
                {bg}
              </button>
            );
          })}
        </div>

        {/* City Input & Availability Toggle */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          <div className="sm:col-span-2 relative">
            <Search className="w-4 h-4 text-stone-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search donors by city, metropolitan region..."
              value={cityFilter}
              onChange={(e) => setCityFilter(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 text-xs rounded-xl bg-white border border-rose-200 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none text-stone-800"
            />
          </div>

          <label className="flex items-center gap-2.5 px-3 py-2 bg-rose-50/40 rounded-xl border border-rose-100 text-xs font-bold text-stone-700 cursor-pointer">
            <input
              type="checkbox"
              checked={onlyAvailable}
              onChange={(e) => setOnlyAvailable(e.target.checked)}
              className="rounded border-rose-300 text-rose-600 focus:ring-rose-500 w-4 h-4"
            />
            <span>Available Donors Only</span>
          </label>
        </div>
      </div>

      {/* Donors Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((donor) => {
          const isRare = ['bombay', 'rh-null', 'kell', 'duffy'].some((r) =>
            donor.blood_group.toLowerCase().includes(r)
          );

          return (
            <div
              key={donor.id}
              className="bg-white border border-rose-100 rounded-xl p-5 shadow-sm hover:border-rose-300 transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-extrabold text-stone-900 text-base">{donor.user?.name || donor.name || 'Verified Donor'}</h3>
                    <p className="text-xs text-stone-500 flex items-center gap-1 mt-0.5">
                      <MapPin className="w-3.5 h-3.5 text-rose-500" />
                      {donor.city}
                    </p>
                  </div>

                  <span className="text-lg font-black px-2.5 py-0.5 rounded-xl bg-rose-100 text-rose-800 border border-rose-200 shrink-0">
                    {donor.blood_group}
                  </span>
                </div>

                {isRare && (
                  <div className="mt-2.5 inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
                    <Sparkles className="w-3 h-3 text-rose-600" />
                    Ultra-Rare Phenotype Registered
                  </div>
                )}

                <div className="mt-3.5 space-y-1 text-xs text-stone-600 bg-rose-50/20 p-2.5 rounded-xl border border-rose-100/60">
                  <p>Age: <strong className="text-stone-800">{donor.age} yrs</strong> • Gender: <strong className="text-stone-800">{donor.gender}</strong></p>
                  <p>Last Donated: <strong className="text-stone-800">{donor.last_donated_date || 'Ready to donate'}</strong></p>
                </div>
              </div>

              <div className="mt-4 pt-3.5 border-t border-rose-100 flex items-center justify-between">
                <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                  donor.is_available
                    ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                    : 'bg-stone-100 text-stone-500'
                }`}>
                  {donor.is_available ? '● Available' : '○ Paused'}
                </span>

                <a
                  href={`tel:${donor.user?.phone || '+18005550199'}`}
                  className="px-3.5 py-1.5 rounded-xl text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 shadow-sm shadow-rose-200 transition flex items-center gap-1.5"
                >
                  <Phone className="w-3.5 h-3.5" />
                  Contact
                </a>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}

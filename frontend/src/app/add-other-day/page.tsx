'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import WorktimeForm from '@/components/WorktimeForm';

export default function AddOtherDayPage() {
  const router = useRouter();
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleDateSelect = () => {
    if (selectedDate) {
      setShowForm(true);
    }
  };

  const handleSuccess = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center">
            <button
              onClick={() => router.push('/dashboard')}
              className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Anderen Tag erfassen</h1>
              <p className="text-sm text-gray-600 mt-1">Wählen Sie ein Datum aus</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!showForm ? (
          <div className="bg-white rounded-xl shadow-md p-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Datum auswählen
            </label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />

            <button
              onClick={handleDateSelect}
              disabled={!selectedDate}
              className="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Weiter
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-md p-8">
            <div className="mb-6 pb-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                {new Date(selectedDate + 'T00:00:00').toLocaleDateString('de-DE', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </h2>
              <button
                onClick={() => setShowForm(false)}
                className="mt-2 text-sm text-blue-600 hover:text-blue-800"
              >
                Datum ändern
              </button>
            </div>

            <WorktimeForm date={selectedDate} onSuccess={handleSuccess} />
          </div>
        )}
      </main>
    </div>
  );
}

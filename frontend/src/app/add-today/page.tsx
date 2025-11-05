'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import WorktimeForm from '@/components/WorktimeForm';

export default function AddTodayPage() {
  const router = useRouter();
  const [entries, setEntries] = useState<number[]>([1]);
  const today = new Date().toISOString().split('T')[0];

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleSuccess = () => {
    router.push('/dashboard');
  };

  const addAnotherEntry = () => {
    setEntries([...entries, entries.length + 1]);
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
              <h1 className="text-2xl font-bold text-gray-900">Heute erfassen</h1>
              <p className="text-sm text-gray-600 mt-1">
                {new Date().toLocaleDateString('de-DE', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {entries.map((entryNum, index) => (
          <div key={entryNum} className="bg-white rounded-xl shadow-md p-8 mb-6">
            {entries.length > 1 && (
              <div className="mb-4 pb-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  Eintrag {index + 1}
                </h2>
              </div>
            )}

            <WorktimeForm
              date={today}
              onSuccess={index === entries.length - 1 ? handleSuccess : undefined}
            />
          </div>
        ))}

        {/* Add Another Entry Button */}
        <div className="text-center">
          <button
            onClick={addAnotherEntry}
            className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition shadow-md"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Weiteren Eintrag hinzufügen
          </button>
        </div>
      </main>
    </div>
  );
}

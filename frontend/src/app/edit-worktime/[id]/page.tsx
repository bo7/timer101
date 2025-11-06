'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams, useSearchParams } from 'next/navigation';
import WorktimeForm from '@/components/WorktimeForm';
import { api, type WorktimeEntry } from '@/lib/api';

export default function EditWorktimePage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const [worktime, setWorktime] = useState<WorktimeEntry | null>(null);
  const [loading, setLoading] = useState(true);

  const id = params.id as string;
  const date = searchParams.get('date') || new Date().toISOString().split('T')[0];

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Fetch the worktime entry
    const fetchWorktime = async () => {
      try {
        const data = await api.getWorktimeById(parseInt(id));
        setWorktime(data);
      } catch (error) {
        console.error('Failed to fetch worktime:', error);
        alert('Fehler beim Laden des Eintrags');
        router.push('/show-day');
      } finally {
        setLoading(false);
      }
    };

    fetchWorktime();
  }, [router, id]);

  const handleSuccess = () => {
    alert('Eintrag erfolgreich aktualisiert!');
    router.push(`/show-day?date=${date}`);
  };

  const handleCancel = () => {
    router.push(`/show-day?date=${date}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Laden...</p>
        </div>
      </div>
    );
  }

  if (!worktime) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center">
            <button
              onClick={handleCancel}
              className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Eintrag bearbeiten</h1>
              <p className="text-sm text-gray-600 mt-1">
                {new Date(date + 'T00:00:00').toLocaleDateString('de-DE', {
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
        <div className="bg-white rounded-xl shadow-md p-8">
          <WorktimeForm
            date={date}
            onSuccess={handleSuccess}
            onCancel={handleCancel}
            initialData={worktime}
          />
        </div>
      </main>
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams, useSearchParams } from 'next/navigation';
import WorktimeForm from '@/components/WorktimeForm';
import { api, type WorktimeEntry } from '@/lib/api';

export default function EditWorktimePage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();

  const worktimeId = parseInt(params.id as string);
  const date = searchParams.get('date') || '';

  const [worktimeData, setWorktimeData] = useState<WorktimeEntry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Fetch worktime data
    const fetchWorktime = async () => {
      try {
        setLoading(true);
        const data = await api.getWorktimeById(worktimeId);
        setWorktimeData(data);
      } catch (error: any) {
        console.error('Failed to fetch worktime:', error);
        setError(error.message || 'Fehler beim Laden der Arbeitszeit');
      } finally {
        setLoading(false);
      }
    };

    if (worktimeId) {
      fetchWorktime();
    }
  }, [worktimeId, router]);

  const handleSuccess = () => {
    router.push(`/show-day?date=${date}`);
  };

  const handleCancel = () => {
    router.push(`/show-day?date=${date}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Lädt...</p>
        </div>
      </div>
    );
  }

  if (error || !worktimeData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center">
              <button
                onClick={handleCancel}
                className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <h1 className="text-xl font-semibold text-gray-800">Fehler</h1>
            </div>
          </div>
        </header>
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error || 'Arbeitszeit konnte nicht geladen werden'}</p>
            <button
              onClick={handleCancel}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Zurück
            </button>
          </div>
        </div>
      </div>
    );
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
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-xl font-semibold text-gray-800">Arbeitszeit bearbeiten</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <WorktimeForm
            date={date}
            onSuccess={handleSuccess}
            onCancel={handleCancel}
            initialData={worktimeData}
          />
        </div>
      </main>
    </div>
  );
}

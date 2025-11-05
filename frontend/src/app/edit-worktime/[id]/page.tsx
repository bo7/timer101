'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams, useSearchParams } from 'next/navigation';
import { api, type WorktimeEntry, type Customer } from '@/lib/api';
import WorktimeForm from '@/components/WorktimeForm';

export default function EditWorktimePage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const worktimeId = parseInt(params.id as string);
  const returnDate = searchParams.get('date');

  const [worktime, setWorktime] = useState<WorktimeEntry | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchWorktime = async () => {
      try {
        const data = await api.getWorktime(worktimeId);
        setWorktime(data);
      } catch (error) {
        console.error('Failed to fetch worktime:', error);
        alert('Fehler beim Laden des Eintrags');
        router.push('/dashboard');
      } finally {
        setLoading(false);
      }
    };

    if (worktimeId) {
      fetchWorktime();
    }
  }, [worktimeId, router]);

  const handleSuccess = () => {
    if (returnDate) {
      router.push(`/show-day?date=${returnDate}`);
    } else {
      router.push('/dashboard');
    }
  };

  const handleCancel = () => {
    if (returnDate) {
      router.push(`/show-day?date=${returnDate}`);
    } else {
      router.push('/dashboard');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!worktime) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Eintrag nicht gefunden</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Zurück zum Dashboard
          </button>
        </div>
      </div>
    );
  }

  const date = worktime.start_time.split('T')[0];

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

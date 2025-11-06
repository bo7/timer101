'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, type WorktimeEntry } from '@/lib/api';

export default function ShowDayPage() {
  const router = useRouter();
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [worktimes, setWorktimes] = useState<WorktimeEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  const fetchWorktimes = async (date: string) => {
    setLoading(true);
    try {
      const data = await api.getWorktimes(date);
      setWorktimes(data);
    } catch (error) {
      console.error('Failed to fetch worktimes:', error);
      alert('Fehler beim Laden der Einträge');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Check for date query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const dateParam = urlParams.get('date');
    if (dateParam) {
      setSelectedDate(dateParam);
      fetchWorktimes(dateParam);
    }
  }, [router]);

  const handleDateChange = (date: string) => {
    setSelectedDate(date);
    if (date) {
      fetchWorktimes(date);
    }
  };

  const handleEdit = (id: number) => {
    setEditingId(id);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Möchten Sie diesen Eintrag wirklich löschen?')) {
      return;
    }

    try {
      await api.deleteWorktime(id);
      setWorktimes(worktimes.filter(wt => wt.id !== id));
    } catch (error: any) {
      alert(error.message || 'Fehler beim Löschen');
    }
  };

  const formatTime = (datetime: string) => {
    return new Date(datetime).toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
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
              <h1 className="text-2xl font-bold text-gray-900">Tag anzeigen</h1>
              <p className="text-sm text-gray-600 mt-1">Erfasste Zeiten ansehen und bearbeiten</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Date Picker */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Datum auswählen
          </label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => handleDateChange(e.target.value)}
            max={new Date().toISOString().split('T')[0]}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
        </div>

        {/* Results */}
        {selectedDate && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Einträge für {new Date(selectedDate + 'T00:00:00').toLocaleDateString('de-DE', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </h2>

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Laden...</p>
              </div>
            ) : worktimes.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p>Keine Einträge für diesen Tag</p>
              </div>
            ) : (
              <div className="space-y-4">
                {worktimes.map((worktime) => (
                  <div
                    key={worktime.id}
                    className={`border rounded-lg p-4 ${
                      worktime.processed
                        ? 'border-gray-300 bg-gray-50'
                        : 'border-blue-200 bg-blue-50'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 text-lg">
                          {worktime.customer_name}
                        </h3>
                        <p className="text-sm text-gray-600">{worktime.location_name}</p>
                      </div>
                      {worktime.processed && (
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Verarbeitet
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                      <div>
                        <span className="text-gray-500">Zeit:</span>
                        <span className="ml-2 font-medium">
                          {formatTime(worktime.start_time)} - {formatTime(worktime.end_time)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Gearbeitet:</span>
                        <span className="ml-2 font-medium">
                          {formatDuration(worktime.worked_minutes || 0)}
                        </span>
                      </div>
                      {worktime.break_minutes > 0 && (
                        <div>
                          <span className="text-gray-500">Pause:</span>
                          <span className="ml-2 font-medium">{worktime.break_minutes} Min</span>
                        </div>
                      )}
                    </div>

                    {worktime.description && (
                      <div className="mb-3 text-sm">
                        <span className="text-gray-500">Tätigkeit:</span>
                        <p className="mt-1 text-gray-700">{worktime.description}</p>
                      </div>
                    )}

                    {!worktime.processed && (
                      <div className="flex gap-2 pt-3 border-t border-gray-200">
                        <button
                          onClick={() => router.push(`/edit-worktime/${worktime.id}?date=${selectedDate}`)}
                          className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition"
                        >
                          Bearbeiten
                        </button>
                        <button
                          onClick={() => handleDelete(worktime.id!)}
                          className="flex-1 px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition"
                        >
                          Löschen
                        </button>
                      </div>
                    )}
                  </div>
                ))}

                {/* Summary */}
                <div className="mt-6 pt-6 border-t border-gray-300">
                  <div className="flex justify-between items-center text-lg font-semibold">
                    <span>Gesamt gearbeitet:</span>
                    <span className="text-blue-600">
                      {formatDuration(worktimes.reduce((sum, wt) => sum + (wt.worked_minutes || 0), 0))}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

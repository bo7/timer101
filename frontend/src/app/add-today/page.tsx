'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import CustomerSearch from '@/components/CustomerSearch';
import LVSearch from '@/components/LVSearch';
import api from '@/lib/api';

interface Customer {
  id: number;
  name: string;
}

interface Baustelle {
  id: number;
  name: string;
}

interface LVEntry {
  id: number;
  position_number?: string;
  description: string;
  is_freitext: boolean;
}

interface PositionEntry {
  id: string;
  lvEntry: LVEntry | null;
  worked_hours: number;
  freitext_description: string;
  is_regie: boolean;
  materials_used: string;
  picture_file: File | null;
  picture_preview: string | null;
  saved: boolean;
}

export default function AddTodayPage() {
  const router = useRouter();
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [baustellen, setBaustellen] = useState<Baustelle[]>([]);
  const [selectedBaustelleId, setSelectedBaustelleId] = useState<number>(0);
  const [positions, setPositions] = useState<PositionEntry[]>([
    {
      id: '1',
      lvEntry: null,
      worked_hours: 8,
      freitext_description: '',
      is_regie: false,
      materials_used: '',
      picture_file: null,
      picture_preview: null,
      saved: false
    }
  ]);
  const today = new Date().toISOString().split('T')[0];

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  useEffect(() => {
    if (selectedCustomer) {
      loadBaustellen();
    }
  }, [selectedCustomer]);

  const loadBaustellen = async () => {
    if (!selectedCustomer) return;
    try {
      const data = await api.getBaustellen(selectedCustomer.id);
      setBaustellen(data);
    } catch (error) {
      console.error('Error loading baustellen:', error);
    }
  };

  const handleCustomerSelect = (customer: Customer) => {
    setSelectedCustomer(customer);
    setSelectedBaustelleId(0);
    // Reset all positions when customer changes
    setPositions([{
      id: Date.now().toString(),
      lvEntry: null,
      worked_hours: 8,
      freitext_description: '',
      is_regie: false,
      materials_used: '',
      picture_file: null,
      picture_preview: null,
      saved: false
    }]);
  };

  const handleBaustelleChange = (baustelleId: number) => {
    setSelectedBaustelleId(baustelleId);
    // Reset all positions when baustelle changes
    setPositions([{
      id: Date.now().toString(),
      lvEntry: null,
      worked_hours: 8,
      freitext_description: '',
      is_regie: false,
      materials_used: '',
      picture_file: null,
      picture_preview: null,
      saved: false
    }]);
  };

  const updatePosition = (id: string, updates: Partial<PositionEntry>) => {
    setPositions(prev => prev.map(p => p.id === id ? { ...p, ...updates } : p));
  };

  const handlePictureSelect = (id: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        updatePosition(id, {
          picture_file: file,
          picture_preview: reader.result as string
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const savePosition = async (position: PositionEntry) => {
    if (!selectedCustomer || !selectedBaustelleId) {
      alert('Bitte wählen Sie Kunde und Baustelle');
      return;
    }

    if (!position.lvEntry) {
      alert('Bitte wählen Sie eine Position');
      return;
    }

    if (position.lvEntry.is_freitext && !position.freitext_description) {
      alert('Bitte geben Sie eine Beschreibung ein');
      return;
    }

    try {
      let picturePath = null;

      // Upload picture if exists
      if (position.picture_file) {
        const formData = new FormData();
        formData.append('file', position.picture_file);

        const uploadResponse = await api.uploadPicture(formData);
        picturePath = uploadResponse.filename;
      }

      // Create worktime entry
      const worktimeData = {
        customer_id: selectedCustomer.id,
        baustelle_id: selectedBaustelleId,
        lv_entry_id: position.lvEntry.is_freitext ? null : position.lvEntry.id,
        date: today,
        worked_hours: position.worked_hours,
        freitext_description: position.lvEntry.is_freitext ? position.freitext_description : null,
        is_regie: position.is_regie,
        materials_used: position.is_regie ? position.materials_used : null,
        picture_path: picturePath
      };

      await api.createWorktime(worktimeData);

      // Mark as saved
      updatePosition(position.id, { saved: true });

    } catch (error: any) {
      alert('Fehler beim Speichern: ' + (error.message || 'Unbekannter Fehler'));
    }
  };

  const addNewPosition = () => {
    setPositions(prev => [...prev, {
      id: Date.now().toString(),
      lvEntry: null,
      worked_hours: 8,
      freitext_description: '',
      is_regie: false,
      materials_used: '',
      picture_file: null,
      picture_preview: null,
      saved: false
    }]);
  };

  const removePosition = (id: string) => {
    setPositions(prev => prev.filter(p => p.id !== id));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
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
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition"
            >
              Fertig
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Fixed Header Section: Customer & Baustelle */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6 sticky top-4 z-10">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Customer Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Kunde *
              </label>
              <CustomerSearch onSelect={handleCustomerSelect} selectedCustomer={selectedCustomer} />
            </div>

            {/* Baustelle Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Baustelle *
              </label>
              <select
                value={selectedBaustelleId}
                onChange={(e) => handleBaustelleChange(Number(e.target.value))}
                disabled={!selectedCustomer}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="0">-- Baustelle wählen --</option>
                {baustellen.map((baustelle) => (
                  <option key={baustelle.id} value={baustelle.id}>
                    {baustelle.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Position Entries */}
        {selectedCustomer && selectedBaustelleId > 0 && (
          <div className="space-y-4">
            {positions.map((position, index) => (
              <div
                key={position.id}
                className={`bg-white rounded-xl shadow-md p-6 ${position.saved ? 'opacity-60' : ''}`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Position {index + 1}
                    {position.saved && <span className="ml-2 text-sm text-green-600">✓ Gespeichert</span>}
                  </h3>
                  {positions.length > 1 && !position.saved && (
                    <button
                      onClick={() => removePosition(position.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                </div>

                {!position.saved && (
                  <div className="space-y-4">
                    {/* LV Entry Search */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Position *
                      </label>
                      <LVSearch
                        baustelleId={selectedBaustelleId}
                        onSelect={(entry) => updatePosition(position.id, { lvEntry: entry })}
                        selectedEntry={position.lvEntry}
                      />
                    </div>

                    {/* Freitext Description */}
                    {position.lvEntry?.is_freitext && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Beschreibung *
                        </label>
                        <textarea
                          value={position.freitext_description}
                          onChange={(e) => updatePosition(position.id, { freitext_description: e.target.value })}
                          rows={3}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Beschreibung eingeben..."
                        />
                      </div>
                    )}

                    {/* Regie Checkbox */}
                    {position.lvEntry?.is_freitext && (
                      <div>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={position.is_regie}
                            onChange={(e) => updatePosition(position.id, { is_regie: e.target.checked })}
                            className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <span className="text-sm font-medium text-gray-700">Regie</span>
                        </label>
                      </div>
                    )}

                    {/* Materials (if Regie) */}
                    {position.is_regie && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Material
                        </label>
                        <textarea
                          value={position.materials_used}
                          onChange={(e) => updatePosition(position.id, { materials_used: e.target.value })}
                          rows={3}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Material eingeben..."
                        />
                      </div>
                    )}

                    {/* Picture Upload (if Regie) */}
                    {position.is_regie && (
                      <div>
                        <label className="flex items-center gap-2 cursor-pointer mb-2">
                          <input
                            type="checkbox"
                            onChange={(e) => {
                              if (e.target.checked) {
                                document.getElementById(`picture-${position.id}`)?.click();
                              } else {
                                updatePosition(position.id, { picture_file: null, picture_preview: null });
                              }
                            }}
                            checked={!!position.picture_file}
                            className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <span className="text-sm font-medium text-gray-700">Bild</span>
                        </label>
                        <input
                          id={`picture-${position.id}`}
                          type="file"
                          accept="image/*"
                          capture="environment"
                          onChange={(e) => handlePictureSelect(position.id, e)}
                          className="hidden"
                        />
                        {position.picture_preview && (
                          <img
                            src={position.picture_preview}
                            alt="Preview"
                            className="mt-2 w-full max-w-xs rounded-lg border"
                          />
                        )}
                      </div>
                    )}

                    {/* Hours */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Arbeitsstunden *
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="8"
                        value={position.worked_hours}
                        onChange={(e) => updatePosition(position.id, { worked_hours: Number(e.target.value) })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    {/* Save Button */}
                    <button
                      onClick={() => savePosition(position)}
                      className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition shadow-md"
                    >
                      Position speichern
                    </button>
                  </div>
                )}
              </div>
            ))}

            {/* Add New Position Button */}
            <div className="text-center">
              <button
                onClick={addNewPosition}
                className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition shadow-md"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Weitere Position hinzufügen
              </button>
            </div>
          </div>
        )}

        {/* Empty State */}
        {(!selectedCustomer || selectedBaustelleId === 0) && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              Bitte wählen Sie zuerst einen Kunden und eine Baustelle aus
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

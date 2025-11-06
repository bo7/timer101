'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, type Customer, type Baustelle, type LVEntry, type WorktimeEntry } from '@/lib/api';
import CustomerSearch from './CustomerSearch';
import LVSearch from './LVSearch';

interface WorktimeFormProps {
  date: string; // YYYY-MM-DD format
  onSuccess?: () => void;
  onCancel?: () => void;
  initialData?: WorktimeEntry;
}

export default function WorktimeForm({ date, onSuccess, onCancel, initialData }: WorktimeFormProps) {
  const router = useRouter();
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [baustellen, setBaustellen] = useState<Baustelle[]>([]);
  const [selectedLVEntry, setSelectedLVEntry] = useState<LVEntry | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const [formData, setFormData] = useState({
    baustelle_id: 0,
    worked_hours: 8,
    freitext_description: '',
  });

  // Load initial data when editing
  useEffect(() => {
    if (initialData) {
      // Update form data with initial values
      setFormData({
        baustelle_id: initialData.baustelle_id || 0,
        worked_hours: initialData.worked_hours || 8,
        freitext_description: initialData.freitext_description || '',
      });

      // Set customer data to pre-populate
      if (initialData.customer_id && initialData.customer_name) {
        setSelectedCustomer({
          id: initialData.customer_id,
          name: initialData.customer_name,
          customer_number: '', // We don't have this in WorktimeEntry
        });
      }

      // Set LV entry if exists
      if (initialData.lv_entry_id && initialData.lv_description) {
        setSelectedLVEntry({
          id: initialData.lv_entry_id,
          baustelle_id: initialData.baustelle_id,
          position_number: initialData.lv_position_number,
          description: initialData.lv_description,
          is_freitext: initialData.lv_description === 'Freitext',
        });
      }
    }
  }, [initialData]);

  // Load baustellen when customer is selected
  useEffect(() => {
    if (selectedCustomer) {
      const fetchBaustellen = async () => {
        try {
          const data = await api.getBaustellen(selectedCustomer.id);
          setBaustellen(data);
          if (data.length > 0 && !formData.baustelle_id) {
            setFormData((prev) => ({ ...prev, baustelle_id: data[0].id }));
          }
        } catch (error) {
          console.error('Failed to fetch baustellen:', error);
        }
      };
      fetchBaustellen();
    } else {
      setBaustellen([]);
      setFormData((prev) => ({ ...prev, baustelle_id: 0 }));
    }
  }, [selectedCustomer]);

  // Warn before leaving with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasChanges]);

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedCustomer) {
      alert('Bitte wählen Sie einen Auftraggeber aus');
      return;
    }

    if (!formData.baustelle_id) {
      alert('Bitte wählen Sie eine Baustelle aus');
      return;
    }

    if (!selectedLVEntry) {
      alert('Bitte wählen Sie eine Position aus');
      return;
    }

    // Validate freitext if "Freitext" is selected
    if (selectedLVEntry.is_freitext && !formData.freitext_description.trim()) {
      alert('Bitte geben Sie eine Beschreibung ein');
      return;
    }

    setLoading(true);

    try {
      const worktimeData: WorktimeEntry = {
        customer_id: selectedCustomer.id,
        baustelle_id: formData.baustelle_id,
        lv_entry_id: selectedLVEntry.is_freitext ? null : selectedLVEntry.id,
        date: date,
        worked_hours: formData.worked_hours,
        freitext_description: selectedLVEntry.is_freitext ? formData.freitext_description : null,
      };

      if (initialData?.id) {
        await api.updateWorktime(initialData.id, worktimeData);
      } else {
        await api.createWorktime(worktimeData);
      }

      setHasChanges(false);
      if (onSuccess) {
        onSuccess();
      } else {
        router.push('/dashboard');
      }
    } catch (error: any) {
      alert(error.message || 'Fehler beim Speichern');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (hasChanges && !confirm('Ungespeicherte Änderungen gehen verloren. Fortfahren?')) {
      return;
    }
    if (onCancel) {
      onCancel();
    } else {
      router.push('/dashboard');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Customer Search */}
      <CustomerSearch onSelect={setSelectedCustomer} selectedCustomer={selectedCustomer} />

      {/* Baustelle */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Baustelle <span className="text-red-500">*</span>
        </label>
        <select
          value={formData.baustelle_id}
          onChange={(e) => handleChange('baustelle_id', parseInt(e.target.value))}
          required
          disabled={baustellen.length === 0}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100"
        >
          <option value="">-- Baustelle wählen --</option>
          {baustellen.map((baustelle) => (
            <option key={baustelle.id} value={baustelle.id}>
              {baustelle.name}
            </option>
          ))}
        </select>
        {selectedCustomer && baustellen.length === 0 && (
          <p className="mt-2 text-sm text-amber-600">Keine Baustellen für diesen Auftraggeber verfügbar</p>
        )}
      </div>

      {/* LV Entry Search */}
      <LVSearch
        baustelleId={formData.baustelle_id || null}
        onSelect={setSelectedLVEntry}
        selectedEntry={selectedLVEntry}
      />

      {/* Freitext Description (only shown when "Freitext" is selected) */}
      {selectedLVEntry?.is_freitext && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tätigkeit <span className="text-red-500">*</span>
          </label>
          <textarea
            value={formData.freitext_description}
            onChange={(e) => handleChange('freitext_description', e.target.value)}
            rows={3}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
            placeholder="Beschreibung der durchgeführten Arbeiten..."
          />
        </div>
      )}

      {/* Worked Hours */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Arbeitsstunden <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          value={formData.worked_hours}
          onChange={(e) => handleChange('worked_hours', parseInt(e.target.value) || 1)}
          min="1"
          max="8"
          required
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
        />
        <p className="mt-1 text-sm text-gray-500">1-8 Stunden</p>
      </div>

      {/* Buttons */}
      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
        >
          {loading ? 'Speichern...' : 'Speichern'}
        </button>
        <button
          type="button"
          onClick={handleCancel}
          className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300 transition"
        >
          Abbrechen
        </button>
      </div>
    </form>
  );
}

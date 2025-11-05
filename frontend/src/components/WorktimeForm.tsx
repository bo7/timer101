'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, type Customer, type Location, type WorktimeEntry } from '@/lib/api';
import CustomerSearch from './CustomerSearch';

interface WorktimeFormProps {
  date: string; // YYYY-MM-DD format
  onSuccess?: () => void;
  onCancel?: () => void;
  initialData?: WorktimeEntry;
}

export default function WorktimeForm({ date, onSuccess, onCancel, initialData }: WorktimeFormProps) {
  const router = useRouter();
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [initialLoading, setInitialLoading] = useState(!!initialData);

  const [formData, setFormData] = useState({
    location_id: initialData?.location_id || 0,
    start_time: initialData?.start_time?.substring(11, 16) || '08:00',
    end_time: initialData?.end_time?.substring(11, 16) || '17:00',
    break_minutes: initialData?.break_minutes || 0,
    description: initialData?.description || '',
  });

  // Load customer data for edit mode
  useEffect(() => {
    if (initialData?.customer_id) {
      const loadCustomer = async () => {
        try {
          // Use the customer info from initialData if available
          if (initialData.customer_name) {
            setSelectedCustomer({
              id: initialData.customer_id,
              name: initialData.customer_name,
              customer_number: '',
            });
          }
        } catch (error) {
          console.error('Failed to load customer:', error);
        } finally {
          setInitialLoading(false);
        }
      };
      loadCustomer();
    } else {
      setInitialLoading(false);
    }
  }, [initialData]);

  // Load locations when customer is selected
  useEffect(() => {
    if (selectedCustomer) {
      const fetchLocations = async () => {
        try {
          const locs = await api.getLocations(selectedCustomer.id);
          setLocations(locs);
          if (locs.length > 0 && !formData.location_id) {
            setFormData((prev) => ({ ...prev, location_id: locs[0].id }));
          }
        } catch (error) {
          console.error('Failed to fetch locations:', error);
        }
      };
      fetchLocations();
    } else {
      setLocations([]);
      setFormData((prev) => ({ ...prev, location_id: 0 }));
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
      alert('Bitte wählen Sie einen Kunden aus');
      return;
    }

    if (!formData.location_id) {
      alert('Bitte wählen Sie einen Standort aus');
      return;
    }

    setLoading(true);

    try {
      const startDateTime = `${date}T${formData.start_time}:00`;
      const endDateTime = `${date}T${formData.end_time}:00`;

      const worktimeData: WorktimeEntry = {
        customer_id: selectedCustomer.id,
        location_id: formData.location_id,
        start_time: startDateTime,
        end_time: endDateTime,
        break_minutes: formData.break_minutes,
        description: formData.description,
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

  if (initialLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Laden...</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Customer Search */}
      <CustomerSearch onSelect={setSelectedCustomer} selectedCustomer={selectedCustomer} />

      {/* Location */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Standort <span className="text-red-500">*</span>
        </label>
        <select
          value={formData.location_id}
          onChange={(e) => handleChange('location_id', parseInt(e.target.value))}
          required
          disabled={locations.length === 0}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100"
        >
          <option value="">-- Standort wählen --</option>
          {locations.map((location) => (
            <option key={location.id} value={location.id}>
              {location.name}
            </option>
          ))}
        </select>
        {selectedCustomer && locations.length === 0 && (
          <p className="mt-2 text-sm text-amber-600">Keine Standorte für diesen Kunden verfügbar</p>
        )}
      </div>

      {/* Start Time */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Startzeit <span className="text-red-500">*</span>
        </label>
        <input
          type="time"
          value={formData.start_time}
          onChange={(e) => handleChange('start_time', e.target.value)}
          required
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
        />
      </div>

      {/* End Time */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Endzeit <span className="text-red-500">*</span>
        </label>
        <input
          type="time"
          value={formData.end_time}
          onChange={(e) => handleChange('end_time', e.target.value)}
          required
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
        />
      </div>

      {/* Break */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Pause (Minuten)
        </label>
        <input
          type="number"
          value={formData.break_minutes}
          onChange={(e) => handleChange('break_minutes', parseInt(e.target.value) || 0)}
          min="0"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
        />
      </div>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Tätigkeit
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          rows={3}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
          placeholder="Beschreibung der durchgeführten Arbeiten..."
        />
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

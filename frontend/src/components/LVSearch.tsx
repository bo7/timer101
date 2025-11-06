'use client';

import { useState, useEffect, useRef } from 'react';
import { api, type LVEntry } from '@/lib/api';

interface LVSearchProps {
  baustelleId: number | null;
  onSelect: (entry: LVEntry | null) => void;
  selectedEntry: LVEntry | null;
}

export default function LVSearch({ baustelleId, onSelect, selectedEntry }: LVSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<LVEntry[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Search LV entries when query changes
  useEffect(() => {
    if (!baustelleId) {
      setResults([]);
      return;
    }

    const searchEntries = async () => {
      setLoading(true);
      try {
        const entries = await api.searchLVEntries(baustelleId, query);
        setResults(entries);
      } catch (error) {
        console.error('Failed to search LV entries:', error);
      } finally {
        setLoading(false);
      }
    };

    searchEntries();
  }, [query, baustelleId]);

  const handleSelect = (entry: LVEntry) => {
    onSelect(entry);
    setQuery(entry.is_freitext ? 'Freitext' : `${entry.position_number || ''} ${entry.description}`.trim());
    setIsOpen(false);
  };

  const handleInputChange = (value: string) => {
    setQuery(value);
    setIsOpen(true);
    if (!value) {
      onSelect(null);
    }
  };

  useEffect(() => {
    if (selectedEntry) {
      setQuery(
        selectedEntry.is_freitext
          ? 'Freitext'
          : `${selectedEntry.position_number || ''} ${selectedEntry.description}`.trim()
      );
    } else {
      setQuery('');
    }
  }, [selectedEntry]);

  return (
    <div ref={wrapperRef} className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Position <span className="text-red-500">*</span>
      </label>

      <input
        type="text"
        value={query}
        onChange={(e) => handleInputChange(e.target.value)}
        onFocus={() => setIsOpen(true)}
        placeholder="Position suchen..."
        disabled={!baustelleId}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-gray-100"
      />

      {!baustelleId && (
        <p className="mt-2 text-sm text-amber-600">Bitte wählen Sie zuerst eine Baustelle</p>
      )}

      {/* Dropdown */}
      {isOpen && baustelleId && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-500">Laden...</div>
          ) : results.length === 0 ? (
            <div className="p-4 text-center text-gray-500">Keine Positionen gefunden</div>
          ) : (
            <ul>
              {results.map((entry) => (
                <li
                  key={entry.id}
                  onClick={() => handleSelect(entry)}
                  className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                >
                  {entry.is_freitext ? (
                    <div className="font-semibold text-green-700">Freitext</div>
                  ) : (
                    <div>
                      <div className="font-semibold text-gray-900">
                        {entry.position_number && (
                          <span className="text-blue-600">{entry.position_number}</span>
                        )}
                      </div>
                      <div className="text-sm text-gray-600">{entry.description}</div>
                      {entry.unit && (
                        <div className="text-xs text-gray-500 mt-1">Einheit: {entry.unit}</div>
                      )}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

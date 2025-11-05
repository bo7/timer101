'use client';

import { useState, useEffect, useRef } from 'react';
import { api, type Customer } from '@/lib/api';

interface CustomerSearchProps {
  onSelect: (customer: Customer) => void;
  selectedCustomer?: Customer | null;
}

export default function CustomerSearch({ onSelect, selectedCustomer }: CustomerSearchProps) {
  const [query, setQuery] = useState(selectedCustomer?.name || '');
  const [results, setResults] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const searchCustomers = async () => {
      if (query.length < 1) {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const customers = await api.searchCustomers(query);
        setResults(customers);
        setShowResults(true);
      } catch (error) {
        console.error('Search failed:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    };

    const debounce = setTimeout(searchCustomers, 300);
    return () => clearTimeout(debounce);
  }, [query]);

  const handleSelect = (customer: Customer) => {
    setQuery(customer.name);
    setShowResults(false);
    onSelect(customer);
  };

  return (
    <div ref={wrapperRef} className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Kunde <span className="text-red-500">*</span>
      </label>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => query && setShowResults(true)}
        placeholder="Kunde suchen..."
        required
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
      />

      {showResults && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-500">Laden...</div>
          ) : results.length > 0 ? (
            results.map((customer) => (
              <button
                key={customer.id}
                type="button"
                onClick={() => handleSelect(customer)}
                className="w-full px-4 py-3 text-left hover:bg-blue-50 border-b border-gray-100 last:border-b-0 transition"
              >
                <div className="font-medium text-gray-900">{customer.name}</div>
                <div className="text-sm text-gray-500">{customer.customer_number}</div>
              </button>
            ))
          ) : (
            <div className="p-4 text-center text-gray-500">
              Keine Kunden gefunden
            </div>
          )}
        </div>
      )}
    </div>
  );
}

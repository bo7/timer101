/**
 * API client for Zeit Erfassung backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface LoginCredentials {
  username: string;
  password: string;
}

interface Customer {
  id: number;
  name: string;
  customer_number: string;
}

interface Baustelle {
  id: number;
  customer_id: number;
  name: string;
  address?: string;
}

interface LVEntry {
  id: number;
  baustelle_id: number;
  position_number?: string;
  description: string;
  unit?: string;
  is_freitext: boolean;
}

interface WorktimeEntry {
  id?: number;
  customer_id: number;
  baustelle_id: number;
  lv_entry_id?: number | null;
  date: string; // YYYY-MM-DD
  worked_hours: number; // 1-8
  freitext_description?: string | null;
  is_regie?: boolean;
  materials_used?: string | null;
  picture_path?: string | null;
  processed?: boolean;
  customer_name?: string;
  baustelle_name?: string;
  lv_position_number?: string;
  lv_description?: string;
}

class ApiClient {
  private getAuthHeader(): HeadersInit {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async login(credentials: LoginCredentials): Promise<{ access_token: string; token_type: string }> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    return data;
  }

  async logout(): Promise<void> {
    localStorage.removeItem('token');
  }

  async getCurrentUser(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }

    return response.json();
  }

  async searchCustomers(query: string): Promise<Customer[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/customers/search?q=${encodeURIComponent(query)}`,
      {
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to search customers');
    }

    return response.json();
  }

  async getBaustellen(customerId: number): Promise<Baustelle[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/baustellen?customer_id=${customerId}`,
      {
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch baustellen');
    }

    return response.json();
  }

  async searchLVEntries(baustelleId: number, query: string = ''): Promise<LVEntry[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/lv/search?baustelle_id=${baustelleId}&q=${encodeURIComponent(query)}`,
      {
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to search LV entries');
    }

    return response.json();
  }

  async getWorktimes(date?: string): Promise<WorktimeEntry[]> {
    const url = date
      ? `${API_BASE_URL}/api/worktimes?date_filter=${date}`
      : `${API_BASE_URL}/api/worktimes`;

    const response = await fetch(url, {
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch worktimes');
    }

    return response.json();
  }

  async getWorktimeById(id: number): Promise<WorktimeEntry> {
    const response = await fetch(`${API_BASE_URL}/api/worktimes/${id}`, {
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch worktime');
    }

    return response.json();
  }

  async createWorktime(worktime: WorktimeEntry): Promise<WorktimeEntry> {
    const response = await fetch(`${API_BASE_URL}/api/worktimes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
      },
      body: JSON.stringify(worktime),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create worktime');
    }

    return response.json();
  }

  async updateWorktime(id: number, worktime: Partial<WorktimeEntry>): Promise<WorktimeEntry> {
    const response = await fetch(`${API_BASE_URL}/api/worktimes/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
      },
      body: JSON.stringify(worktime),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update worktime');
    }

    return response.json();
  }

  async deleteWorktime(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/worktimes/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete worktime');
    }
  }

  async uploadPicture(formData: FormData): Promise<{ filename: string; size: number; content_type: string }> {
    const response = await fetch(`${API_BASE_URL}/api/uploads/picture`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload picture');
    }

    return response.json();
  }
}

export const api = new ApiClient();
export type { Customer, Baustelle, LVEntry, WorktimeEntry };

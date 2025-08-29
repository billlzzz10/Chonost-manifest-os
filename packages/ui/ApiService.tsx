// API Service สำหรับการเชื่อมต่อกับ Backend
const API_BASE_URL = 'http://localhost:5000/api';

export interface Manuscript {
  id: number;
  title: string;
  content: string;
  characters: string[];
  word_count: number;
  created_at: string;
  updated_at: string;
}

export interface ManuscriptAnalysis {
  word_count: number;
  character_count: number;
  paragraph_count: number;
  estimated_reading_time: number;
  detected_characters: string[];
  mood: string;
  themes: string[];
  writing_style: string;
}

export class ApiService {
  // ดึงรายการ manuscripts ทั้งหมด
  static async getManuscripts(): Promise<{ manuscripts: Manuscript[]; total: number }> {
    try {
      const response = await fetch(`${API_BASE_URL}/manuscripts`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching manuscripts:', error);
      throw error;
    }
  }

  // ดึง manuscript ตาม ID
  static async getManuscript(id: number): Promise<Manuscript> {
    try {
      const response = await fetch(`${API_BASE_URL}/manuscripts/${id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching manuscript:', error);
      throw error;
    }
  }

  // สร้าง manuscript ใหม่
  static async createManuscript(data: {
    title: string;
    content: string;
    characters?: string[];
  }): Promise<Manuscript> {
    try {
      const response = await fetch(`${API_BASE_URL}/manuscripts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error creating manuscript:', error);
      throw error;
    }
  }

  // อัปเดต manuscript
  static async updateManuscript(id: number, data: {
    title?: string;
    content?: string;
    characters?: string[];
  }): Promise<Manuscript> {
    try {
      const response = await fetch(`${API_BASE_URL}/manuscripts/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error updating manuscript:', error);
      throw error;
    }
  }

  // วิเคราะห์ manuscript
  static async analyzeManuscript(id: number): Promise<ManuscriptAnalysis> {
    try {
      const response = await fetch(`${API_BASE_URL}/manuscripts/${id}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error analyzing manuscript:', error);
      throw error;
    }
  }

  // ส่งออก manuscript
  static async exportManuscript(id: number, format: 'json' | 'markdown' | 'txt' = 'json'): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/manuscripts/${id}/export?format=${format}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      if (format === 'json') {
        return await response.json();
      } else {
        return await response.text();
      }
    } catch (error) {
      console.error('Error exporting manuscript:', error);
      throw error;
    }
  }

  // Auto-save function สำหรับ Advanced Editor
  static async autoSave(id: number, content: string, title?: string): Promise<void> {
    try {
      await this.updateManuscript(id, { content, title });
      console.log('Auto-saved successfully');
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
  }
}


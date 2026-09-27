const API_BASE_URL = "http://127.0.0.1:5000";

function getAuthHeaders(isJson = true) {
  const token = localStorage.getItem("healthchain_token");
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (isJson) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

export const api = {
  // Authentication
  async login(username, password) {
    const res = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Failed to log in");
    return data;
  },

  async register(username, password, role) {
    const res = await fetch(`${API_BASE_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, role })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Registration rejected");
    return data;
  },

  // Patient Records
  async getMyRecords() {
    const res = await fetch(`${API_BASE_URL}/get_my_records`, {
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to fetch patient records");
    return data;
  },

  async uploadRecord(file, patientId, prediction = "Not Evaluated") {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("patient_id", patientId);
    formData.append("prediction", prediction);

    const res = await fetch(`${API_BASE_URL}/upload_record`, {
      method: "POST",
      headers: getAuthHeaders(false),
      body: formData
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || data.message || "Upload failed");
    return data;
  },

  async grantAccess(recordId, doctorId) {
    const res = await fetch(`${API_BASE_URL}/grant_access`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ record_id: recordId, doctor_id: doctorId })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to grant access");
    return data;
  },

  // Doctor Operations
  async getRecordsByDoctor() {
    const res = await fetch(`${API_BASE_URL}/get_records_by_doctor`, {
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to fetch doctor records");
    return data;
  },

  async extractVitals(ipfsHash) {
    const res = await fetch(`${API_BASE_URL}/extract_vitals`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ ipfs_hash: ipfsHash })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Extraction failed");
    return data;
  },

  async predict(vitals) {
    const res = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ vitals })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Prediction computation failed");
    return data;
  },

  async createPredictionRecord({ patientId, vitals, doctorNotes, targetEhrId }) {
    const res = await fetch(`${API_BASE_URL}/create_prediction_record`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        patient_id: patientId,
        vitals,
        doctor_notes: doctorNotes,
        target_ehr_id: targetEhrId
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || data.message || "Failed to anchor record to blockchain");
    return data;
  },

  async downloadReport(recordId) {
    const res = await fetch(`${API_BASE_URL}/download_report/${recordId}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error("Failed to download PDF from IPFS");
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `clinical_report_${recordId}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },

  // Admin Operations
  async getAdminStats() {
    const res = await fetch(`${API_BASE_URL}/admin/stats`, {
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Failed to fetch admin stats");
    return data;
  },

  async getAdminUsers() {
    const res = await fetch(`${API_BASE_URL}/admin/users`, {
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Failed to fetch users");
    return data;
  },

  async getDockerStatus() {
    const res = await fetch(`${API_BASE_URL}/admin/docker_status`, {
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Failed to fetch docker status");
    return data;
  }
};

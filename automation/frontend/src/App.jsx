import { useState, useEffect } from 'react';
import './App.css';
import Login from './Login';
function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('rpa_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [activeTab, setActiveTab] = useState('dashboard');
  const [status, setStatus] = useState({ is_running: false, log: '' });
  const [loading, setLoading] = useState(false);
  const [speed, setSpeed] = useState(0.5);
  const [settingsTab, setSettingsTab] = useState('buyer');
  const [files, setFiles] = useState({ identity_doc: null, income_doc: null, bank_doc: null, seller_identity_doc: null });
  const [propFiles, setPropFiles] = useState({ p_img: null, p_own: null });
  const [formData, setFormData] = useState({ task: 'auto_approve', param1: '', apply_cat: 'All', apply_loc: '', apply_type: '', p_title: '', p_price: '', p_cat: 'Rent', p_type: 'Apartment', p_loc: '', p_beds: '', p_baths: '', p_area: '', p_floor: '', p_tfloors: '', p_desc: '', p_furn: 'Semi Furnished', p_facing: 'North', p_am: '', p_map: '' });
  const [exportAppCount, setExportAppCount] = useState(0);
  const [buyerApprovedCount, setBuyerApprovedCount] = useState(0);

  const handleAmenityChange = (e) => {
    const value = e.target.value;
    const currentList = formData.p_am ? formData.p_am.split(',').filter(Boolean) : [];
    if (e.target.checked) {
      setFormData({ ...formData, p_am: [...currentList, value].join(',') });
    } else {
      setFormData({ ...formData, p_am: currentList.filter(v => v !== value).join(',') });
    }
  };

  // Sync user to localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem('rpa_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('rpa_user');
    }
  }, [user]);

  // Polling status
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/status');
        if (res.ok) setStatus(await res.json());
      } catch (err) { }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  // Check matching applications count for export filter
  useEffect(() => {
    if (formData.task === 'export_csv') {
      const activeFilter = formData.param1 || 'Approved Only';
      fetch(`http://127.0.0.1:8000/api/applications/count?filter=${encodeURIComponent(activeFilter)}`)
        .then(res => res.json())
        .then(data => setExportAppCount(data.count || 0))
        .catch(() => setExportAppCount(0));
    }
  }, [formData.task, formData.param1, status.last_run_status, status.is_running]);

  // Check matching approved properties for buyer
  useEffect(() => {
    if (formData.task === 'buyer_export') {
      const email = user?.plotify_email || '';
      fetch(`http://127.0.0.1:8000/api/buyer/approved-count?email=${encodeURIComponent(email)}`)
        .then(res => res.json())
        .then(data => setBuyerApprovedCount(data.count || 0))
        .catch(() => setBuyerApprovedCount(0));
    }
  }, [formData.task, user?.plotify_email, status.last_run_status, status.is_running]);

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append('user_id', user.user_id);
      fd.append('plotify_email', user.plotify_email || '');
      fd.append('plotify_password', user.plotify_password || '');
      fd.append('seller_plotify_email', user.seller_plotify_email || '');
      fd.append('seller_plotify_password', user.seller_plotify_password || '');
      fd.append('buyer_name', user.buyer_name || '');
      fd.append('buyer_phone', user.buyer_phone || '');
      fd.append('buyer_budget', user.buyer_budget || '');
      fd.append('buyer_occupation', user.buyer_occupation || '');
      fd.append('buyer_moving_date', user.buyer_moving_date || '');
      fd.append('buyer_message', user.buyer_message || '');

      fd.append('existing_identity', user.buyer_identity_doc || '');
      fd.append('existing_income', user.buyer_income_doc || '');
      fd.append('existing_bank', user.buyer_bank_doc || '');

      fd.append('seller_title', user.seller_title || '');
      fd.append('seller_price', user.seller_price || '');
      fd.append('seller_category', user.seller_category || '');
      fd.append('seller_location', user.seller_location || '');
      fd.append('seller_description', user.seller_description || '');
      fd.append('seller_bedrooms', user.seller_bedrooms || '');
      fd.append('seller_bathrooms', user.seller_bathrooms || '');
      fd.append('seller_area', user.seller_area || '');
      fd.append('seller_type', user.seller_type || '');
      fd.append('seller_owner_name', user.seller_owner_name || '');
      fd.append('seller_phone', user.seller_phone || '');
      fd.append('seller_email', user.seller_email || '');
      fd.append('seller_amenities', user.seller_amenities || '');
      fd.append('seller_map_link', user.seller_map_link || '');
      fd.append('seller_floor', user.seller_floor || '');
      fd.append('seller_total_floors', user.seller_total_floors || '');
      fd.append('seller_furnishing', user.seller_furnishing || '');
      fd.append('seller_facing', user.seller_facing || '');

      fd.append('existing_s_id', user.seller_identity_doc || '');

      if (files.identity_doc) fd.append('identity_doc', files.identity_doc);
      if (files.income_doc) fd.append('income_doc', files.income_doc);
      if (files.bank_doc) fd.append('bank_doc', files.bank_doc);
      if (files.seller_identity_doc) fd.append('seller_identity_doc', files.seller_identity_doc);

      const res = await fetch('http://127.0.0.1:8000/api/settings', {
        method: 'POST',
        body: fd
      });

      const data = await res.json();

      if (res.ok) {
        setUser(data);
        alert('Personal Info saved successfully!');
      } else {
        if (res.status === 404) {
          alert('User session not found in database (database was reset). Please sign up or log in.');
          setUser(null);
          localStorage.removeItem('rpa_user');
          return;
        }
        console.error('Validation error:', data);
        alert('Error saving personal info: ' + JSON.stringify(data.detail || data));
      }
    } catch (err) {
      alert("Error saving personal info");
    }
    setLoading(false);
  };

  const handleRunBot = async (taskName) => {
    const isSellerTask = taskName === 'auto_list' || taskName === 'auto_approve' || taskName === 'auto_list_bulk' || taskName === 'export_csv';
    const emailToUse = isSellerTask ? user.seller_plotify_email : user.plotify_email;
    const passToUse = isSellerTask ? user.seller_plotify_password : user.plotify_password;

    if (!emailToUse || !passToUse) {
      alert(`Please configure your ${isSellerTask ? 'Seller' : 'Buyer'} Plotify credentials in the Personal Info tab.`);
      setActiveTab('settings');
      return;
    }

    try {
      const fd = new FormData();
      fd.append('speed', speed);
      fd.append('task', taskName);
      fd.append('email', emailToUse);
      fd.append('password', passToUse);
      fd.append('param1', formData.param1);
      fd.append('user_id', user.user_id);

      if (taskName === 'auto_list') {
        fd.append('p_title', formData.p_title);
        fd.append('p_price', formData.p_price);
        fd.append('p_cat', formData.p_cat);
        fd.append('p_type', formData.p_type);
        fd.append('p_loc', formData.p_loc);
        fd.append('p_beds', formData.p_beds);
        fd.append('p_baths', formData.p_baths);
        fd.append('p_area', formData.p_area);
        fd.append('p_floor', formData.p_floor);
        fd.append('p_tfloors', formData.p_tfloors);
        fd.append('p_desc', formData.p_desc);
        fd.append('p_furn', formData.p_furn);
        fd.append('p_facing', formData.p_facing);
        fd.append('p_am', formData.p_am);
        fd.append('p_map', formData.p_map);
        if (propFiles.p_img) fd.append('p_img', propFiles.p_img);
        if (propFiles.p_own) fd.append('p_own', propFiles.p_own);
      } else if (taskName === 'auto_list_bulk') {
        if (propFiles.bulk_csv) fd.append('csv_file', propFiles.bulk_csv);
      } else if (taskName === 'auto_apply') {
        fd.append('apply_cat', formData.apply_cat || 'All');
        fd.append('apply_loc', formData.apply_loc || '');
        fd.append('apply_type', formData.apply_type || '');
        fd.append('apply_budget', formData.param1 || '');
      }

      await fetch('http://127.0.0.1:8000/api/run', {
        method: 'POST',
        body: fd
      });
    } catch (err) { }
  };

  const handleStopBot = async () => {
    await fetch('http://127.0.0.1:8000/api/stop', { method: 'POST' });
  };

  if (!user || !user.user_id) {
    return <Login onLogin={(u) => setUser(u)} />;
  }

  return (
    <div className="crm-layout">
      <aside className="sidebar">
        <div className="logo">BizLink RPA</div>
        <nav className="nav-menu">
          <div className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
            <span>⌂</span> Dashboard
          </div>
          <div className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}>
            <span>👤</span> Personal Info
          </div>
        </nav>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-title">
            <span>{activeTab === 'dashboard' ? '📊 Automation Dashboard' : '👤 Personal Info & Credentials'}</span>
          </div>
          <div className="topbar-actions">
            <span className="user-badge">👤 {user.email}</span>
            <button className="primary-btn" onClick={() => setUser(null)} style={{ padding: '5px 12px', background: '#F1F5F9', color: '#0F172A', border: '1px solid #E2E8F0' }}>Log out</button>
          </div>
        </header>

        <div className="view-container">

          {activeTab === 'dashboard' && (
            <div className="dashboard-grid">

              {/* TASKS SECTION */}
              <div className="form-card">
                <div className="form-card-header">
                  <h2>Run Automations</h2>
                </div>

                <div className="tasks-grid">
                  <div className={`k-card ${formData.task === 'auto_approve' ? 'dark' : ''}`} onClick={() => setFormData({ ...formData, task: 'auto_approve', param1: '' })}>
                    <h4>Seller: Auto-Approve</h4>
                    <p>Approve incoming apps</p>
                  </div>
                  <div className={`k-card ${formData.task === 'export_csv' ? 'dark' : ''}`} onClick={() => setFormData({ ...formData, task: 'export_csv', param1: 'Approved Only' })}>
                    <h4>Seller: Export CSV</h4>
                    <p>Export apps & properties</p>
                  </div>
                  <div className={`k-card ${formData.task === 'auto_list' ? 'dark' : ''}`} onClick={() => setFormData({ ...formData, task: 'auto_list', param1: '' })}>
                    <h4>Seller: List Property</h4>
                    <p>Auto-post new listing</p>
                  </div>
                  <div className={`k-card ${formData.task === 'auto_list_bulk' ? 'dark' : ''}`} onClick={() => setFormData({ ...formData, task: 'auto_list_bulk', param1: '' })}>
                    <h4>Seller: Bulk List</h4>
                    <p>Post from CSV file</p>
                  </div>
                  <div className={`k-card ${formData.task === 'auto_apply' ? 'dark' : ''}`} onClick={() => setFormData({ ...formData, task: 'auto_apply', param1: '' })}>
                    <h4>Buyer: Smart Apply</h4>
                    <p>Apply with saved profile</p>
                  </div>
                  <div className={`k-card ${formData.task === 'buyer_export' ? 'dark' : ''}`} onClick={() => setFormData({ ...formData, task: 'buyer_export', param1: '' })}>
                    <h4>Buyer: Export Approved</h4>
                    <p>Download approved rentals</p>
                  </div>
                </div>

                {formData.task === 'auto_approve' && (
                  <div className="input-group">
                    <label>Minimum Score (0 - 100%)</label>
                    <input type="number" value={formData.param1} onChange={(e) => setFormData({ ...formData, param1: e.target.value })} placeholder="75" />
                  </div>
                )}

                {formData.task === 'export_csv' && (
                  <div className="task-detail-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <h4>Export Applications to CSV Automation</h4>
                      {exportAppCount > 0 ? (
                        <a
                          href={`http://127.0.0.1:8000/api/download/approval-report?filter=${encodeURIComponent(formData.param1 || 'Approved Only')}`}
                          download="approved_applications_report.csv"
                          target="_blank"
                          rel="noreferrer"
                          style={{ fontSize: '0.78rem', color: '#10b981', textDecoration: 'none', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '4px', background: '#ecfdf5', padding: '4px 10px', borderRadius: '6px', border: '1px solid #a7f3d0' }}
                        >
                          📥 Download Latest CSV
                        </a>
                      ) : (
                        <span style={{ fontSize: '0.78rem', color: '#ef4444', background: '#fef2f2', padding: '4px 10px', borderRadius: '6px', border: '1px solid #fecaca', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          ⚠️ No application detected
                        </span>
                      )}
                    </div>
                    <p>
                      This dedicated automation logs into your Seller portal, scans all processed applications, extracts applicant details (Name, Email, Phone, Income, Employment) and their linked Property details (Title, Rent), and compiles them into a clean CSV spreadsheet.
                    </p>
                    <div className="input-group">
                      <label>Export Filter</label>
                      <select
                        value={formData.param1 || 'Approved Only'}
                        onChange={(e) => setFormData({ ...formData, param1: e.target.value })}
                      >
                        <option value="Approved Only">Approved Only (Recommended)</option>
                        <option value="All">All Processed (Approved & Rejected)</option>
                      </select>
                    </div>
                  </div>
                )}

                {formData.task === 'auto_list_bulk' && (
                  <div className="task-detail-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <h4>Upload Properties CSV</h4>
                      <a href="/bulk_property_rules.pdf" download style={{ fontSize: '0.78rem', color: '#3b82f6', textDecoration: 'none', fontWeight: 'bold' }}>
                        <i className="fa-solid fa-download"></i> Download CSV Rulebook (PDF)
                      </a>
                    </div>
                    <p>Upload a CSV file containing property details. The bot will automatically loop through and list every property.</p>
                    <div className="input-group">
                      <label>CSV File</label>
                      <input type="file" accept=".csv" onChange={(e) => setPropFiles({ ...propFiles, bulk_csv: e.target.files[0] })} />
                    </div>
                  </div>
                )}

                {formData.task === 'auto_list' && (
                  <div className="task-detail-card">
                    <h4 style={{ marginTop: 0, marginBottom: '10px' }}>New Property Listing Details</h4>
                    <div className="form-grid">
                      <div className="input-group">
                        <label>Property Title</label>
                        <input type="text" value={formData.p_title} onChange={(e) => setFormData({ ...formData, p_title: e.target.value })} />
                      </div>
                      <div className="input-group">
                        <label>Price (₹)</label>
                        <input type="number" value={formData.p_price} onChange={(e) => setFormData({ ...formData, p_price: e.target.value })} />
                      </div>
                      <div className="input-group">
                        <label>Category</label>
                        <select style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }} value={formData.p_cat} onChange={(e) => setFormData({ ...formData, p_cat: e.target.value })}>
                          <option value="Sell">Sell</option>
                          <option value="Rent">Rent</option>
                          <option value="Commercial">Commercial</option>
                        </select>
                      </div>
                      <div className="input-group">
                        <label>Type</label>
                        <select style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }} value={formData.p_type} onChange={(e) => setFormData({ ...formData, p_type: e.target.value })}>
                          <option value="House">House</option>
                          <option value="Apartment">Apartment</option>
                          <option value="Villa">Villa</option>
                          <option value="Commercial">Commercial</option>
                          <option value="Farm House">Farm House</option>
                          <option value="Beach House">Beach House</option>
                        </select>
                      </div>
                      <div className="input-group">
                        <label>Location</label>
                        <input type="text" value={formData.p_loc} onChange={(e) => setFormData({ ...formData, p_loc: e.target.value })} />
                      </div>
                      <div className="input-group">
                        <label>Bedrooms</label>
                        <input type="number" value={formData.p_beds} onChange={(e) => setFormData({ ...formData, p_beds: e.target.value })} />
                      </div>
                      <div className="input-group">
                        <label>Bathrooms</label>
                        <input type="number" value={formData.p_baths} onChange={(e) => setFormData({ ...formData, p_baths: e.target.value })} />
                      </div>
                      <div className="input-group">
                        <label>Area (sqft)</label>
                        <input type="text" value={formData.p_area} onChange={(e) => setFormData({ ...formData, p_area: e.target.value })} />
                      </div>
                      <div className="input-group">
                        <label>Property Floor No.</label>
                        <input type="number" value={formData.p_floor} onChange={(e) => setFormData({ ...formData, p_floor: e.target.value })} />
                      </div>
                      <div className="input-group">
                        <label>Total Floors</label>
                        <input type="number" value={formData.p_tfloors} onChange={(e) => setFormData({ ...formData, p_tfloors: e.target.value })} />
                      </div>
                      <div className="input-group">
                        <label>Furnishing</label>
                        <select style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }} value={formData.p_furn} onChange={(e) => setFormData({ ...formData, p_furn: e.target.value })}>
                          <option value="Unfurnished">Unfurnished</option>
                          <option value="Semi Furnished">Semi Furnished</option>
                          <option value="Fully Furnished">Fully Furnished</option>
                        </select>
                      </div>
                      <div className="input-group">
                        <label>Facing</label>
                        <select style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }} value={formData.p_facing} onChange={(e) => setFormData({ ...formData, p_facing: e.target.value })}>
                          <option value="North">North</option>
                          <option value="South">South</option>
                          <option value="East">East</option>
                          <option value="West">West</option>
                        </select>
                      </div>
                    </div>

                    <div className="form-grid full" style={{ marginTop: '15px' }}>
                      <div className="input-group">
                        <label>Amenities</label>
                        <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
                          {["Lift", "Parking", "Power Backup", "Security", "Water Supply", "Play Area"].map(am => (
                            <label key={am} style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
                              <input type="checkbox" value={am} checked={(formData.p_am || '').split(',').includes(am)} onChange={handleAmenityChange} />
                              {am === "Play Area" ? "Children Play Area" : am}
                            </label>
                          ))}
                        </div>
                      </div>
                      <div className="input-group">
                        <label>Map Link URL</label>
                        <input type="text" value={formData.p_map} onChange={(e) => setFormData({ ...formData, p_map: e.target.value })} />
                      </div>
                    </div>

                    <div className="input-group" style={{ marginTop: '15px' }}>
                      <label>Description</label>
                      <textarea style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', resize: 'vertical' }} rows="2" value={formData.p_desc} onChange={(e) => setFormData({ ...formData, p_desc: e.target.value })}></textarea>
                    </div>

                    <div className="form-grid full" style={{ marginTop: '15px' }}>
                      <div className="input-group">
                        <label>Property Image File</label>
                        <input type="file" onChange={(e) => setPropFiles({ ...propFiles, p_img: e.target.files[0] })} />
                      </div>
                      <div className="input-group">
                        <label>Ownership Proof Document</label>
                        <input type="file" onChange={(e) => setPropFiles({ ...propFiles, p_own: e.target.files[0] })} />
                      </div>
                    </div>
                  </div>
                )}

                {formData.task === 'auto_apply' && (
                  <div className="task-detail-card">
                    <h4 style={{ marginTop: 0, marginBottom: '8px' }}>Smart Apply Search & Budget Filters</h4>
                    <p style={{ marginBottom: '15px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      Configure your property criteria. The RPA bot will log in, navigate to Plotify across your selected categories (Rent, Buy, and Commercial), apply these filters directly, and submit applications for all matching properties using your saved profile.
                    </p>
                    <div className="form-grid">
                      <div className="input-group">
                        <label>Category</label>
                        <select
                          style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}
                          value={formData.apply_cat || 'All'}
                          onChange={(e) => setFormData({ ...formData, apply_cat: e.target.value })}
                        >
                          <option value="All">All Categories (Rent, Buy & Commercial)</option>
                          <option value="Rent">Rent</option>
                          <option value="Buy">Buy</option>
                          <option value="Commercial">Commercial</option>
                        </select>
                      </div>
                      <div className="input-group">
                        <label>Property Type</label>
                        <select
                          style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}
                          value={formData.apply_type || ''}
                          onChange={(e) => setFormData({ ...formData, apply_type: e.target.value })}
                        >
                          <option value="">All Types</option>
                          {(!formData.apply_cat || formData.apply_cat === 'All' || formData.apply_cat === 'Rent' || formData.apply_cat === 'Buy') && (
                            <>
                              <option value="Apartment">Apartment</option>
                              <option value="House">House</option>
                            </>
                          )}
                          {(!formData.apply_cat || formData.apply_cat === 'All' || formData.apply_cat === 'Buy') && (
                            <option value="Land">Land</option>
                          )}
                          {(!formData.apply_cat || formData.apply_cat === 'All' || formData.apply_cat === 'Commercial') && (
                            <>
                              <option value="Office Space">Office Space</option>
                              <option value="Retail Shop">Retail Shop</option>
                              <option value="Warehouse">Warehouse</option>
                              <option value="Commercial Building">Commercial Building</option>
                              <option value="Commercial">Commercial</option>
                            </>
                          )}
                        </select>
                      </div>
                      <div className="input-group">
                        <label>Preferred City or Area</label>
                        <input
                          type="text"
                          value={formData.apply_loc || ''}
                          onChange={(e) => setFormData({ ...formData, apply_loc: e.target.value })}
                          placeholder="e.g. Downtown (or leave empty for Any)"
                        />
                      </div>
                      <div className="input-group">
                        <label>Maximum Budget (₹)</label>
                        <input
                          type="number"
                          value={formData.param1 || ''}
                          onChange={(e) => setFormData({ ...formData, param1: e.target.value })}
                          placeholder="Any Budget (e.g. 25000)"
                          min="0"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {formData.task === 'buyer_export' && (
                  <div className="task-detail-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <h4>Approved Rental Properties Report</h4>
                      {buyerApprovedCount > 0 ? (
                        <a
                          href={`http://127.0.0.1:8000/api/buyer/download-approved?email=${encodeURIComponent(user?.plotify_email || '')}`}
                          download="buyer_approved_properties.csv"
                          target="_blank"
                          rel="noreferrer"
                          style={{ fontSize: '0.78rem', color: '#10b981', textDecoration: 'none', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '4px', background: '#ecfdf5', padding: '4px 10px', borderRadius: '6px', border: '1px solid #a7f3d0' }}
                        >
                          📥 Download Approved Properties CSV
                        </a>
                      ) : (
                        <span style={{ fontSize: '0.78rem', color: '#ef4444', background: '#fef2f2', padding: '4px 10px', borderRadius: '6px', border: '1px solid #fecaca', fontWeight: 'bold', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          ⚠️ No approved applications detected
                        </span>
                      )}
                    </div>
                    <p>
                      This dedicated automation logs into your Buyer portal, reviews all rental applications submitted for your account, and extracts all properties where the owner/seller has marked your application as Approved — compiling property details (Title, Location, Amount) and landlord contact details (Owner Name, Phone, Email) into a clean spreadsheet.
                    </p>
                  </div>
                )}

                <div className="input-group" style={{ marginTop: '16px' }}>
                  <label>Execution Speed: {speed}s delay</label>
                  <input type="range" min="0" max="2" step="0.1" value={speed} onChange={(e) => setSpeed(e.target.value)} />
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
                  <button className="primary-btn" style={{ flex: 1 }} onClick={() => handleRunBot(formData.task)} disabled={status.is_running}>▶ Run Bot</button>
                  <button className="primary-btn btn-danger" style={{ flex: 1 }} onClick={handleStopBot} disabled={!status.is_running}>⏹ Stop</button>
                </div>

                {status.is_running && <div style={{ marginTop: '12px', color: '#10b981', fontWeight: '600', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}><span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }}></span> Bot is currently running...</div>}

                {status.last_run_status && (
                  <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                    <div style={{ fontSize: '0.82rem' }}>
                      <span style={{ fontWeight: '600', marginRight: '6px' }}>Last Run:</span>
                      <span className="badge" style={{ background: status.last_run_status === 'success' ? '#dcfce3' : '#fee2e2', color: status.last_run_status === 'success' ? '#166534' : '#991b1b' }}>
                        {status.last_run_status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* ACTIVITY SECTION */}
              <div className="form-card" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="form-card-header">
                  <h2>Live Activity Logs</h2>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <a href="http://127.0.0.1:8000/api/report" target="_blank" rel="noreferrer" style={{ color: '#64748b', fontSize: '0.78rem', textDecoration: 'none', fontWeight: 500 }}>📄 Report</a>
                    <a href="http://127.0.0.1:8000/api/log" target="_blank" rel="noreferrer" style={{ color: '#64748b', fontSize: '0.78rem', textDecoration: 'none', fontWeight: 500 }}>📋 Logs</a>
                  </div>
                </div>

                <div className="terminal-window" style={{ flex: 1, marginTop: '2px' }}>
                  <div className="terminal-header">
                    <div className="terminal-dots">
                      <div className="terminal-dot dot-red"></div>
                      <div className="terminal-dot dot-yellow"></div>
                      <div className="terminal-dot dot-green"></div>
                    </div>
                    <div className="terminal-title">bizlink-bot-runner ~ bash</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: status.is_running ? '#22c55e' : '#94a3b8', display: 'inline-block' }}></span>
                      <span style={{ fontSize: '0.68rem', color: status.is_running ? '#22c55e' : '#94a3b8', fontFamily: 'JetBrains Mono, monospace' }}>{status.is_running ? 'RUNNING' : 'IDLE'}</span>
                    </div>
                  </div>
                  <pre className="terminal">
                    {status.logs || 'No recent activity...'}
                  </pre>
                </div>
              </div>

            </div>
          )}

          {activeTab === 'settings' && (
            <div className="personal-info-container">
              {/* Header with Title & Profile Switcher */}
              <div className="personal-info-header">
                <div>
                  <h2 className="personal-info-title">Personal Info & Bot Credentials</h2>
                  <p className="personal-info-subtitle">Configure your Plotify portal credentials and identity details used by automation bots.</p>
                </div>
                <div className="profile-switcher">
                  <button
                    type="button"
                    onClick={() => setSettingsTab('buyer')}
                    className={`profile-pill-btn ${settingsTab === 'buyer' ? 'active' : ''}`}
                  >
                    👤 Buyer Profile
                  </button>
                  <button
                    type="button"
                    onClick={() => setSettingsTab('seller')}
                    className={`profile-pill-btn ${settingsTab === 'seller' ? 'active' : ''}`}
                  >
                    🏠 Seller Profile
                  </button>
                </div>
              </div>

              <form onSubmit={handleSaveSettings} className="personal-info-form">
                {settingsTab === 'buyer' && (
                  <div className="info-sections-grid">
                    {/* Section 1: Plotify Portal Credentials */}
                    <div className="info-section-card">
                      <div className="info-section-title-row">
                        <span className="section-icon">🔐</span>
                        <div>
                          <h3>Plotify Portal Credentials (Buyer)</h3>
                          <p>The RPA bot securely authenticates with Plotify using these login credentials.</p>
                        </div>
                      </div>
                      <div className="form-grid">
                        <div className="input-group">
                          <label>Plotify Buyer Email</label>
                          <input
                            type="email"
                            placeholder="buyer@plotify.in"
                            value={user.plotify_email || ''}
                            onChange={(e) => setUser({ ...user, plotify_email: e.target.value })}
                            required
                          />
                        </div>
                        <div className="input-group">
                          <label>Plotify Buyer Password</label>
                          <input
                            type="password"
                            placeholder="••••••••••••"
                            value={user.plotify_password || ''}
                            onChange={(e) => setUser({ ...user, plotify_password: e.target.value })}
                            required
                          />
                        </div>
                      </div>
                    </div>

                    {/* Section 2: Personal Profile Details */}
                    <div className="info-section-card">
                      <div className="info-section-title-row">
                        <span className="section-icon">📋</span>
                        <div>
                          <h3>Applicant Profile & Background</h3>
                          <p>Automated applications will auto-fill your profile details into landlord screening forms.</p>
                        </div>
                      </div>
                      <div className="form-grid">
                        <div className="input-group">
                          <label>Full Legal Name</label>
                          <input
                            type="text"
                            placeholder="e.g. John Doe"
                            value={user.buyer_name || ''}
                            onChange={(e) => setUser({ ...user, buyer_name: e.target.value })}
                          />
                        </div>
                        <div className="input-group">
                          <label>Phone Number</label>
                          <input
                            type="text"
                            placeholder="+91 98765 43210"
                            value={user.buyer_phone || ''}
                            onChange={(e) => setUser({ ...user, buyer_phone: e.target.value })}
                          />
                        </div>
                        <div className="input-group">
                          <label>Monthly Income (₹)</label>
                          <input
                            type="text"
                            placeholder="e.g. 50000"
                            value={user.buyer_budget || ''}
                            onChange={(e) => setUser({ ...user, buyer_budget: e.target.value })}
                          />
                        </div>
                        <div className="input-group">
                          <label>Employment Status</label>
                          <select
                            value={user.buyer_occupation || 'Employed'}
                            onChange={(e) => setUser({ ...user, buyer_occupation: e.target.value })}
                          >
                            <option value="Employed">Employed (Full-Time)</option>
                            <option value="Self-Employed">Self-Employed</option>
                            <option value="Student">Student</option>
                            <option value="Unemployed">Unemployed / Other</option>
                          </select>
                        </div>
                      </div>
                      <div className="input-group" style={{ marginTop: '12px' }}>
                        <label>Application Cover Note / Message (Optional)</label>
                        <textarea
                          rows="2"
                          placeholder="Brief message introducing yourself to landlords..."
                          value={user.buyer_message || ''}
                          onChange={(e) => setUser({ ...user, buyer_message: e.target.value })}
                        />
                      </div>
                    </div>

                    {/* Section 3: Verification Documents */}
                    <div className="info-section-card">
                      <div className="info-section-title-row">
                        <span className="section-icon">📁</span>
                        <div>
                          <h3>Verification & KYC Documents</h3>
                          <p>Required for screening score verification. Files are stored securely for automated submission.</p>
                        </div>
                      </div>
                      <div className="docs-upload-grid">
                        <div className="doc-item-box">
                          <div className="doc-item-header">
                            <span className="doc-icon">🪪</span>
                            <span className="doc-label">Govt ID (Aadhar / PAN)</span>
                          </div>
                          {user.buyer_identity_doc ? (
                            <span className="doc-status-badge success" title={user.buyer_identity_doc}>
                              ✓ {user.buyer_identity_doc.split('/').pop().split('\\').pop()}
                            </span>
                          ) : (
                            <span className="doc-status-badge pending">Not uploaded yet</span>
                          )}
                          <input
                            type="file"
                            onChange={(e) => setFiles({ ...files, identity_doc: e.target.files[0] })}
                          />
                        </div>

                        <div className="doc-item-box">
                          <div className="doc-item-header">
                            <span className="doc-icon">📄</span>
                            <span className="doc-label">Proof of Income</span>
                          </div>
                          {user.buyer_income_doc ? (
                            <span className="doc-status-badge success" title={user.buyer_income_doc}>
                              ✓ {user.buyer_income_doc.split('/').pop().split('\\').pop()}
                            </span>
                          ) : (
                            <span className="doc-status-badge pending">Not uploaded yet</span>
                          )}
                          <input
                            type="file"
                            onChange={(e) => setFiles({ ...files, income_doc: e.target.files[0] })}
                          />
                        </div>

                        <div className="doc-item-box">
                          <div className="doc-item-header">
                            <span className="doc-icon">🏦</span>
                            <span className="doc-label">Bank Statement</span>
                          </div>
                          {user.buyer_bank_doc ? (
                            <span className="doc-status-badge success" title={user.buyer_bank_doc}>
                              ✓ {user.buyer_bank_doc.split('/').pop().split('\\').pop()}
                            </span>
                          ) : (
                            <span className="doc-status-badge pending">Not uploaded yet</span>
                          )}
                          <input
                            type="file"
                            onChange={(e) => setFiles({ ...files, bank_doc: e.target.files[0] })}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {settingsTab === 'seller' && (
                  <div className="info-sections-grid">
                    {/* Section 1: Seller Plotify Portal Credentials */}
                    <div className="info-section-card">
                      <div className="info-section-title-row">
                        <span className="section-icon">🔐</span>
                        <div>
                          <h3>Plotify Portal Credentials (Seller)</h3>
                          <p>The RPA listing bot will use this account to automatically post and manage listings.</p>
                        </div>
                      </div>
                      <div className="form-grid">
                        <div className="input-group">
                          <label>Plotify Seller Email</label>
                          <input
                            type="email"
                            placeholder="seller@plotify.in"
                            value={user.seller_plotify_email || ''}
                            onChange={(e) => setUser({ ...user, seller_plotify_email: e.target.value })}
                            required
                          />
                        </div>
                        <div className="input-group">
                          <label>Plotify Seller Password</label>
                          <input
                            type="password"
                            placeholder="••••••••••••"
                            value={user.seller_plotify_password || ''}
                            onChange={(e) => setUser({ ...user, seller_plotify_password: e.target.value })}
                            required
                          />
                        </div>
                      </div>
                    </div>

                    {/* Section 2: Owner & Contact Profile */}
                    <div className="info-section-card">
                      <div className="info-section-title-row">
                        <span className="section-icon">🏠</span>
                        <div>
                          <h3>Owner Profile & Contact Details</h3>
                          <p>These contact details are automatically attached to all published property listings.</p>
                        </div>
                      </div>
                      <div className="form-grid">
                        <div className="input-group">
                          <label>Owner Full Name</label>
                          <input
                            type="text"
                            placeholder="e.g. Robert Smith"
                            value={user.seller_owner_name || ''}
                            onChange={(e) => setUser({ ...user, seller_owner_name: e.target.value })}
                          />
                        </div>
                        <div className="input-group">
                          <label>Contact Phone</label>
                          <input
                            type="text"
                            placeholder="+91 98765 43210"
                            value={user.seller_phone || ''}
                            onChange={(e) => setUser({ ...user, seller_phone: e.target.value })}
                          />
                        </div>
                        <div className="input-group">
                          <label>Contact Email</label>
                          <input
                            type="email"
                            placeholder="owner@example.com"
                            value={user.seller_email || ''}
                            onChange={(e) => setUser({ ...user, seller_email: e.target.value })}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Section 3: Seller Identity Verification */}
                    <div className="info-section-card">
                      <div className="info-section-title-row">
                        <span className="section-icon">🪪</span>
                        <div>
                          <h3>Seller Verification Document</h3>
                          <p>Upload proof of identity or ownership for verified landlord status.</p>
                        </div>
                      </div>
                      <div className="doc-item-box" style={{ maxWidth: '360px' }}>
                        <div className="doc-item-header">
                          <span className="doc-icon">🪪</span>
                          <span className="doc-label">Seller Identity Doc (Aadhar / PAN)</span>
                        </div>
                        {user.seller_identity_doc ? (
                          <span className="doc-status-badge success" title={user.seller_identity_doc}>
                            ✓ {user.seller_identity_doc.split('/').pop().split('\\').pop()}
                          </span>
                        ) : (
                          <span className="doc-status-badge pending">Not uploaded yet</span>
                        )}
                        <input
                          type="file"
                          onChange={(e) => setFiles({ ...files, seller_identity_doc: e.target.files[0] })}
                        />
                      </div>
                    </div>
                  </div>
                )}

                <div className="save-bar">
                  <button type="submit" className="primary-btn save-btn" disabled={loading}>
                    {loading ? 'Saving...' : '💾 Save Personal Info'}
                  </button>
                </div>
              </form>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}

export default App;

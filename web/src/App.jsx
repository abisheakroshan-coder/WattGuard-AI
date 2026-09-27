import React, { useState } from 'react';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Alerts from './pages/Alerts';
import ConsumerList from './pages/ConsumerList';
import ConsumerDetail from './pages/ConsumerDetail';
import InspectionQueue from './pages/InspectionQueue';
import FieldOperations from './pages/FieldOperations';
import Analytics from './pages/Analytics';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedConsumerId, setSelectedConsumerId] = useState('CONS_COM_001');
  const [fieldInitialConsumer, setFieldInitialConsumer] = useState('');
  const [toastMessage, setToastMessage] = useState('');

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 5000);
  };

  const handleSelectConsumer = (cid) => {
    setSelectedConsumerId(cid);
    setActiveTab('consumer-detail');
  };

  const handleNavigateToField = (cid) => {
    setFieldInitialConsumer(cid);
    setActiveTab('field-ops');
  };

  const handleTriggerBatch = async () => {
    try {
      const res = await api.runBatchScoring({ limit: 50 });
      showToast(
        `Batch Scoring Complete: ${res.evaluated_meters_count} meters evaluated, ${res.alerts_generated_count} active alerts synced in ${res.execution_time_seconds}s.`
      );
    } catch (err) {
      showToast(`Batch scoring error: ${err.message}`);
    }
  };

  return (
    <div className="app-container">
      {/* SCADA Telemetry Header */}
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        selectedConsumerId={selectedConsumerId}
        onTriggerBatch={handleTriggerBatch}
      />

      {/* Main Content Viewport */}
      <main className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard
            onSelectConsumer={handleSelectConsumer}
            onNavigate={setActiveTab}
          />
        )}

        {activeTab === 'alerts' && (
          <Alerts onSelectConsumer={handleSelectConsumer} />
        )}

        {activeTab === 'consumers' && (
          <ConsumerList onSelectConsumer={handleSelectConsumer} />
        )}

        {activeTab === 'consumer-detail' && (
          <ConsumerDetail
            consumerId={selectedConsumerId}
            onNavigateToField={handleNavigateToField}
          />
        )}

        {activeTab === 'queue' && (
          <InspectionQueue onSelectConsumer={handleSelectConsumer} />
        )}

        {activeTab === 'field-ops' && (
          <FieldOperations initialConsumerId={fieldInitialConsumer || selectedConsumerId} />
        )}

        {activeTab === 'analytics' && <Analytics />}
      </main>

      {/* Global Toast */}
      {toastMessage && (
        <div className="toast-container">
          <div className="toast">
            <span className="led-indicator led-cyan"></span>
            <span style={{ fontSize: '0.75rem' }}>{toastMessage}</span>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { Save, Bell, DollarSign, Clock, Key, Moon, Sun } from 'lucide-react';
import { useStore } from '../lib/store';

export function Settings() {
  const { theme, toggleTheme } = useStore();
  const [settings, setSettings] = useState({
    // Notification settings
    emailNotifications: true,
    slackNotifications: false,
    snsNotifications: false,
    emailAddress: '',
    slackWebhook: '',
    snsTopicArn: '',
    
    // Approval settings
    autoApprovalThreshold: 100,
    prodEnvironmentApproval: true,
    requireManualApproval: false,
    
    // Soft delete settings
    softDeleteEnabled: true,
    softDeleteTTL: 7,
    createSnapshots: true,
    snapshotThresholdGB: 10,
    
    // API settings
    apiEndpoint: 'http://localhost:8000',
    apiTimeout: 30,
    retryAttempts: 3,
  });

  const [saved, setSaved] = useState(false);

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('aws-nuker-settings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem('aws-nuker-settings', JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const updateSetting = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Settings</h1>
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          Save Settings
        </button>
      </div>

      {saved && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          Settings saved successfully!
        </div>
      )}

      {/* Theme Settings */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          {theme === 'dark' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
          <h2 className="text-xl font-semibold">Appearance</h2>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Theme</label>
            <button
              onClick={toggleTheme}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600"
            >
              {theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
            </button>
          </div>
        </div>
      </div>

      {/* Notification Settings */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Bell className="w-5 h-5" />
          <h2 className="text-xl font-semibold">Notifications</h2>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Email Notifications</label>
            <input
              type="checkbox"
              checked={settings.emailNotifications}
              onChange={(e) => updateSetting('emailNotifications', e.target.checked)}
              className="w-4 h-4 rounded"
            />
          </div>
          {settings.emailNotifications && (
            <div>
              <label className="block text-sm font-medium mb-2">Email Address</label>
              <input
                type="email"
                value={settings.emailAddress}
                onChange={(e) => updateSetting('emailAddress', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
                placeholder="user@example.com"
              />
            </div>
          )}

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Slack Notifications</label>
            <input
              type="checkbox"
              checked={settings.slackNotifications}
              onChange={(e) => updateSetting('slackNotifications', e.target.checked)}
              className="w-4 h-4 rounded"
            />
          </div>
          {settings.slackNotifications && (
            <div>
              <label className="block text-sm font-medium mb-2">Slack Webhook URL</label>
              <input
                type="text"
                value={settings.slackWebhook}
                onChange={(e) => updateSetting('slackWebhook', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
                placeholder="https://hooks.slack.com/services/..."
              />
            </div>
          )}

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">SNS Notifications</label>
            <input
              type="checkbox"
              checked={settings.snsNotifications}
              onChange={(e) => updateSetting('snsNotifications', e.target.checked)}
              className="w-4 h-4 rounded"
            />
          </div>
          {settings.snsNotifications && (
            <div>
              <label className="block text-sm font-medium mb-2">SNS Topic ARN</label>
              <input
                type="text"
                value={settings.snsTopicArn}
                onChange={(e) => updateSetting('snsTopicArn', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
                placeholder="arn:aws:sns:us-east-1:123456789012:topic"
              />
            </div>
          )}
        </div>
      </div>

      {/* Approval Settings */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <DollarSign className="w-5 h-5" />
          <h2 className="text-xl font-semibold">Approval Workflow</h2>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Auto-Approval Cost Threshold ($)
            </label>
            <input
              type="number"
              value={settings.autoApprovalThreshold}
              onChange={(e) => updateSetting('autoApprovalThreshold', Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
              min="0"
            />
            <p className="text-xs text-gray-500 mt-1">
              Deletions below this cost will be auto-approved
            </p>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Require Approval for Production</label>
              <p className="text-xs text-gray-500">Always require manual approval for prod resources</p>
            </div>
            <input
              type="checkbox"
              checked={settings.prodEnvironmentApproval}
              onChange={(e) => updateSetting('prodEnvironmentApproval', e.target.checked)}
              className="w-4 h-4 rounded"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Require Manual Approval (All)</label>
              <p className="text-xs text-gray-500">Override auto-approval for all deletions</p>
            </div>
            <input
              type="checkbox"
              checked={settings.requireManualApproval}
              onChange={(e) => updateSetting('requireManualApproval', e.target.checked)}
              className="w-4 h-4 rounded"
            />
          </div>
        </div>
      </div>

      {/* Soft Delete Settings */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Clock className="w-5 h-5" />
          <h2 className="text-xl font-semibold">Soft Delete & Snapshots</h2>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Enable Soft Delete</label>
              <p className="text-xs text-gray-500">Resources marked for deletion with recovery window</p>
            </div>
            <input
              type="checkbox"
              checked={settings.softDeleteEnabled}
              onChange={(e) => updateSetting('softDeleteEnabled', e.target.checked)}
              className="w-4 h-4 rounded"
            />
          </div>

          {settings.softDeleteEnabled && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Soft Delete TTL (days)
              </label>
              <input
                type="number"
                value={settings.softDeleteTTL}
                onChange={(e) => updateSetting('softDeleteTTL', Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
                min="1"
                max="30"
              />
              <p className="text-xs text-gray-500 mt-1">
                Time window for recovery before permanent deletion
              </p>
            </div>
          )}

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Create Pre-Deletion Snapshots</label>
              <p className="text-xs text-gray-500">Snapshot resources before deletion</p>
            </div>
            <input
              type="checkbox"
              checked={settings.createSnapshots}
              onChange={(e) => updateSetting('createSnapshots', e.target.checked)}
              className="w-4 h-4 rounded"
            />
          </div>

          {settings.createSnapshots && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Snapshot Threshold (GB)
              </label>
              <input
                type="number"
                value={settings.snapshotThresholdGB}
                onChange={(e) => updateSetting('snapshotThresholdGB', Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
                min="0"
              />
              <p className="text-xs text-gray-500 mt-1">
                Create snapshots for resources larger than this size
              </p>
            </div>
          )}
        </div>
      </div>

      {/* API Settings */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <Key className="w-5 h-5" />
          <h2 className="text-xl font-semibold">API Configuration</h2>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">API Endpoint</label>
            <input
              type="text"
              value={settings.apiEndpoint}
              onChange={(e) => updateSetting('apiEndpoint', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
              placeholder="http://localhost:8000"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Request Timeout (seconds)
            </label>
            <input
              type="number"
              value={settings.apiTimeout}
              onChange={(e) => updateSetting('apiTimeout', Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
              min="5"
              max="300"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Retry Attempts
            </label>
            <input
              type="number"
              value={settings.retryAttempts}
              onChange={(e) => updateSetting('retryAttempts', Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700"
              min="0"
              max="10"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

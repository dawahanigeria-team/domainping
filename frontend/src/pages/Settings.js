import React, { useState } from 'react';
import { 
  EnvelopeIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { notificationAPI } from '../services/api';
import toast from 'react-hot-toast';

const Settings = () => {
  const [emailTest, setEmailTest] = useState({ email: '', loading: false });
  const [smsTest, setSmsTest] = useState({ phone: '', loading: false });
  const [desktopTest, setDesktopTest] = useState({ loading: false });

  const handleEmailTest = async (e) => {
    e.preventDefault();
    if (!emailTest.email) {
      toast.error('Please enter an email address');
      return;
    }

    try {
      setEmailTest(prev => ({ ...prev, loading: true }));
      await notificationAPI.testEmail(emailTest.email);
      toast.success('Test email sent successfully! Check your inbox.');
    } catch (error) {
      console.error('Email test failed:', error);
      toast.error('Failed to send test email. Check your configuration.');
    } finally {
      setEmailTest(prev => ({ ...prev, loading: false }));
    }
  };

  const handleSmsTest = async (e) => {
    e.preventDefault();
    if (!smsTest.phone) {
      toast.error('Please enter a phone number');
      return;
    }

    try {
      setSmsTest(prev => ({ ...prev, loading: true }));
      await notificationAPI.testSMS(smsTest.phone);
      toast.success('Test SMS sent successfully!');
    } catch (error) {
      console.error('SMS test failed:', error);
      toast.error('Failed to send test SMS. Check your Twilio configuration.');
    } finally {
      setSmsTest(prev => ({ ...prev, loading: false }));
    }
  };

  const handleDesktopTest = async () => {
    try {
      setDesktopTest({ loading: true });
      await notificationAPI.testDesktop();
      toast.success('Desktop notification sent!');
    } catch (error) {
      console.error('Desktop test failed:', error);
      toast.error('Failed to send desktop notification.');
    } finally {
      setDesktopTest({ loading: false });
    }
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-600">
          Configure your notification preferences and test your setup
        </p>
      </div>

      <div className="space-y-8">
        {/* Email Configuration */}
        <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <div className="flex items-center">
                <EnvelopeIcon className="h-6 w-6 text-primary-600 mr-2" />
                <h3 className="text-lg font-medium leading-6 text-gray-900">
                  Email Notifications
                </h3>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Test your email configuration and send a sample notification
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <form onSubmit={handleEmailTest} className="space-y-4">
                <div>
                  <label htmlFor="test-email" className="block text-sm font-medium text-gray-700">
                    Test Email Address
                  </label>
                  <div className="mt-1 flex rounded-md shadow-sm">
                    <input
                      type="email"
                      id="test-email"
                      value={emailTest.email}
                      onChange={(e) => setEmailTest(prev => ({ ...prev, email: e.target.value }))}
                      className="flex-1 focus:ring-primary-500 focus:border-primary-500 block w-full min-w-0 rounded-l-md sm:text-sm border-gray-300"
                      placeholder="test@example.com"
                    />
                    <button
                      type="submit"
                      disabled={emailTest.loading}
                      className="inline-flex items-center px-4 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 text-sm hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50"
                    >
                      {emailTest.loading ? 'Sending...' : 'Send Test'}
                    </button>
                  </div>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                  <div className="flex">
                    <InformationCircleIcon className="h-5 w-5 text-blue-400" />
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-blue-800">
                        Email Configuration Required
                      </h3>
                      <div className="mt-2 text-sm text-blue-700">
                        <p>Make sure you have configured the following in your .env file:</p>
                        <ul className="list-disc list-inside mt-1 space-y-1">
                          <li>SMTP_SERVER (e.g., smtp.gmail.com)</li>
                          <li>SMTP_PORT (e.g., 587)</li>
                          <li>SMTP_USERNAME (your email)</li>
                          <li>SMTP_PASSWORD (app password)</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* SMS Configuration */}
        <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <div className="flex items-center">
                <DevicePhoneMobileIcon className="h-6 w-6 text-primary-600 mr-2" />
                <h3 className="text-lg font-medium leading-6 text-gray-900">
                  SMS Notifications
                </h3>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Test your Twilio SMS configuration
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <form onSubmit={handleSmsTest} className="space-y-4">
                <div>
                  <label htmlFor="test-phone" className="block text-sm font-medium text-gray-700">
                    Test Phone Number
                  </label>
                  <div className="mt-1 flex rounded-md shadow-sm">
                    <input
                      type="tel"
                      id="test-phone"
                      value={smsTest.phone}
                      onChange={(e) => setSmsTest(prev => ({ ...prev, phone: e.target.value }))}
                      className="flex-1 focus:ring-primary-500 focus:border-primary-500 block w-full min-w-0 rounded-l-md sm:text-sm border-gray-300"
                      placeholder="+1234567890"
                    />
                    <button
                      type="submit"
                      disabled={smsTest.loading}
                      className="inline-flex items-center px-4 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 text-sm hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:opacity-50"
                    >
                      {smsTest.loading ? 'Sending...' : 'Send Test'}
                    </button>
                  </div>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                  <div className="flex">
                    <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-yellow-800">
                        Twilio Configuration Required
                      </h3>
                      <div className="mt-2 text-sm text-yellow-700">
                        <p>SMS notifications require a Twilio account. Configure these in your .env file:</p>
                        <ul className="list-disc list-inside mt-1 space-y-1">
                          <li>TWILIO_ACCOUNT_SID</li>
                          <li>TWILIO_AUTH_TOKEN</li>
                          <li>TWILIO_PHONE_NUMBER</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* Desktop Notifications */}
        <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <div className="flex items-center">
                <ComputerDesktopIcon className="h-6 w-6 text-primary-600 mr-2" />
                <h3 className="text-lg font-medium leading-6 text-gray-900">
                  Desktop Notifications
                </h3>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Test native desktop notifications
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <div className="space-y-4">
                <button
                  onClick={handleDesktopTest}
                  disabled={desktopTest.loading}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {desktopTest.loading ? 'Sending...' : 'Send Test Notification'}
                </button>
                <div className="bg-green-50 border border-green-200 rounded-md p-4">
                  <div className="flex">
                    <CheckCircleIcon className="h-5 w-5 text-green-400" />
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-green-800">
                        Desktop Notifications Ready
                      </h3>
                      <div className="mt-2 text-sm text-green-700">
                        <p>Desktop notifications work out of the box. Make sure to allow notifications when prompted by your browser or operating system.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Default Settings */}
        <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Default Settings
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Configure default notification preferences for new domains
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <div className="space-y-6">
                <fieldset>
                  <legend className="text-base font-medium text-gray-900">Default Notification Types</legend>
                  <div className="mt-4 space-y-4">
                    <div className="flex items-center">
                      <input
                        id="default-email"
                        name="default-notifications"
                        type="checkbox"
                        defaultChecked
                        className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                      />
                      <label htmlFor="default-email" className="ml-3 block text-sm font-medium text-gray-700">
                        Email Notifications
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        id="default-desktop"
                        name="default-notifications"
                        type="checkbox"
                        defaultChecked
                        className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                      />
                      <label htmlFor="default-desktop" className="ml-3 block text-sm font-medium text-gray-700">
                        Desktop Notifications
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        id="default-sms"
                        name="default-notifications"
                        type="checkbox"
                        className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                      />
                      <label htmlFor="default-sms" className="ml-3 block text-sm font-medium text-gray-700">
                        SMS Notifications
                      </label>
                    </div>
                  </div>
                </fieldset>

                <div>
                  <label htmlFor="default-reminder-days" className="block text-sm font-medium text-gray-700">
                    Default Reminder Days
                  </label>
                  <input
                    type="text"
                    id="default-reminder-days"
                    defaultValue="90,30,14,7,3,1"
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Comma-separated list of days before expiration to send reminders
                  </p>
                </div>

                <div>
                  <label htmlFor="notification-time" className="block text-sm font-medium text-gray-700">
                    Notification Time
                  </label>
                  <input
                    type="time"
                    id="notification-time"
                    defaultValue="09:00"
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Time of day to send daily notifications (24-hour format)
                  </p>
                </div>

                <div className="flex justify-end">
                  <button
                    type="button"
                    className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Reset to Defaults
                  </button>
                  <button
                    type="button"
                    className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Save Settings
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 
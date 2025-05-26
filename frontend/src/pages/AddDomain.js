import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { 
  ArrowLeftIcon,
  InformationCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { domainAPI } from '../services/api';
import toast from 'react-hot-toast';

const AddDomain = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [fetchingWhois, setFetchingWhois] = useState(false);
  
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors }
  } = useForm({
    defaultValues: {
      email_notifications: true,
      desktop_notifications: true,
      sms_notifications: false,
      auto_renew: false,
      renewal_period_years: 1,
      custom_reminder_days: '90,30,14,7,3,1'
    }
  });

  const domainName = watch('name');

  const fetchWhoisData = async () => {
    if (!domainName) {
      toast.error('Please enter a domain name first');
      return;
    }

    try {
      setFetchingWhois(true);
      // Create a temporary domain to fetch WHOIS data
      const tempDomain = await domainAPI.createDomain({
        name: domainName,
        expiration_date: new Date().toISOString()
      });
      
      // Refresh WHOIS data
      const updatedDomain = await domainAPI.refreshWhois(tempDomain.data.id);
      
      // Delete the temporary domain
      await domainAPI.deleteDomain(tempDomain.data.id);
      
      // Populate form with WHOIS data
      if (updatedDomain.data.expiration_date) {
        setValue('expiration_date', updatedDomain.data.expiration_date.split('T')[0]);
      }
      if (updatedDomain.data.registrar) {
        setValue('registrar', updatedDomain.data.registrar);
      }
      if (updatedDomain.data.admin_email) {
        setValue('admin_email', updatedDomain.data.admin_email);
      }
      
      toast.success('WHOIS data fetched successfully');
    } catch (error) {
      console.error('Failed to fetch WHOIS data:', error);
      toast.error('Failed to fetch WHOIS data. Please enter details manually.');
    } finally {
      setFetchingWhois(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      
      // Convert date string to ISO format
      const formData = {
        ...data,
        expiration_date: new Date(data.expiration_date).toISOString(),
        renewal_cost: data.renewal_cost ? parseFloat(data.renewal_cost) : null
      };
      
      await domainAPI.createDomain(formData);
      toast.success('Domain added successfully!');
      navigate('/domains');
    } catch (error) {
      console.error('Failed to create domain:', error);
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error('Failed to add domain. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back
        </button>
        <h1 className="mt-2 text-2xl font-semibold text-gray-900">Add Domain</h1>
        <p className="mt-1 text-sm text-gray-600">
          Add a new domain to your renewal reminder system
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          {/* Domain Information */}
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Domain Information
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Basic information about your domain
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <div className="grid grid-cols-6 gap-6">
                <div className="col-span-6">
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Domain Name *
                  </label>
                  <div className="mt-1 flex rounded-md shadow-sm">
                    <input
                      type="text"
                      {...register('name', { 
                        required: 'Domain name is required',
                        pattern: {
                          value: /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$/,
                          message: 'Please enter a valid domain name'
                        }
                      })}
                      className="flex-1 focus:ring-primary-500 focus:border-primary-500 block w-full min-w-0 rounded-md sm:text-sm border-gray-300"
                      placeholder="example.com"
                    />
                    <button
                      type="button"
                      onClick={fetchWhoisData}
                      disabled={fetchingWhois || !domainName}
                      className="ml-3 inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                    >
                      {fetchingWhois ? (
                        <ArrowPathIcon className="h-4 w-4 animate-spin" />
                      ) : (
                        'Fetch WHOIS'
                      )}
                    </button>
                  </div>
                  {errors.name && (
                    <p className="mt-2 text-sm text-red-600">{errors.name.message}</p>
                  )}
                </div>

                <div className="col-span-6 sm:col-span-3">
                  <label htmlFor="expiration_date" className="block text-sm font-medium text-gray-700">
                    Expiration Date *
                  </label>
                  <input
                    type="date"
                    {...register('expiration_date', { required: 'Expiration date is required' })}
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                  />
                  {errors.expiration_date && (
                    <p className="mt-2 text-sm text-red-600">{errors.expiration_date.message}</p>
                  )}
                </div>

                <div className="col-span-6 sm:col-span-3">
                  <label htmlFor="registrar" className="block text-sm font-medium text-gray-700">
                    Registrar
                  </label>
                  <input
                    type="text"
                    {...register('registrar')}
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                    placeholder="GoDaddy, Namecheap, etc."
                  />
                </div>

                <div className="col-span-6 sm:col-span-3">
                  <label htmlFor="renewal_cost" className="block text-sm font-medium text-gray-700">
                    Renewal Cost ($)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    {...register('renewal_cost')}
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                    placeholder="15.99"
                  />
                </div>

                <div className="col-span-6 sm:col-span-3">
                  <label htmlFor="renewal_period_years" className="block text-sm font-medium text-gray-700">
                    Renewal Period (Years)
                  </label>
                  <select
                    {...register('renewal_period_years')}
                    className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  >
                    <option value={1}>1 Year</option>
                    <option value={2}>2 Years</option>
                    <option value={3}>3 Years</option>
                    <option value={5}>5 Years</option>
                    <option value={10}>10 Years</option>
                  </select>
                </div>

                <div className="col-span-6">
                  <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                    Notes
                  </label>
                  <textarea
                    {...register('notes')}
                    rows={3}
                    className="mt-1 shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border border-gray-300 rounded-md"
                    placeholder="Any additional notes about this domain..."
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Contact Information
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Contact details for notifications
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <div className="grid grid-cols-6 gap-6">
                <div className="col-span-6 sm:col-span-3">
                  <label htmlFor="admin_email" className="block text-sm font-medium text-gray-700">
                    Admin Email
                  </label>
                  <input
                    type="email"
                    {...register('admin_email')}
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                    placeholder="admin@example.com"
                  />
                </div>

                <div className="col-span-6 sm:col-span-3">
                  <label htmlFor="admin_phone" className="block text-sm font-medium text-gray-700">
                    Admin Phone
                  </label>
                  <input
                    type="tel"
                    {...register('admin_phone')}
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                    placeholder="+1234567890"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <h3 className="text-lg font-medium leading-6 text-gray-900">
                Notification Settings
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Configure how you want to be notified
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <div className="space-y-6">
                <fieldset>
                  <legend className="text-base font-medium text-gray-900">Notification Types</legend>
                  <div className="mt-4 space-y-4">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        {...register('email_notifications')}
                        className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                      />
                      <label className="ml-3 block text-sm font-medium text-gray-700">
                        Email Notifications
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        {...register('desktop_notifications')}
                        className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                      />
                      <label className="ml-3 block text-sm font-medium text-gray-700">
                        Desktop Notifications
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        {...register('sms_notifications')}
                        className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                      />
                      <label className="ml-3 block text-sm font-medium text-gray-700">
                        SMS Notifications
                      </label>
                    </div>
                  </div>
                </fieldset>

                <div>
                  <label htmlFor="custom_reminder_days" className="block text-sm font-medium text-gray-700">
                    Reminder Days
                  </label>
                  <input
                    type="text"
                    {...register('custom_reminder_days')}
                    className="mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                    placeholder="90,30,14,7,3,1"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Comma-separated list of days before expiration to send reminders
                  </p>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    {...register('auto_renew')}
                    className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                  />
                  <label className="ml-3 block text-sm font-medium text-gray-700">
                    Auto-renewal enabled
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {loading ? 'Adding...' : 'Add Domain'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddDomain; 
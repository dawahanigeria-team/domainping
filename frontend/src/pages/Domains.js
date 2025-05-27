import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { 
  PlusIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  PencilIcon,
  TrashIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { domainAPI } from '../services/api';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

const Domains = () => {
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [refreshingId, setRefreshingId] = useState(null);

  const fetchDomains = useCallback(async () => {
    try {
      setLoading(true);
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (statusFilter) params.status_filter = statusFilter;
      
      const response = await domainAPI.getDomains(params);
      setDomains(response.data);
    } catch (error) {
      console.error('Failed to fetch domains:', error);
      toast.error('Failed to load domains');
    } finally {
      setLoading(false);
    }
  }, [searchTerm, statusFilter]);

  useEffect(() => {
    fetchDomains();
  }, [fetchDomains]);

  const handleRefreshWhois = async (domainId) => {
    try {
      setRefreshingId(domainId);
      await domainAPI.refreshWhois(domainId);
      toast.success('WHOIS data refreshed successfully');
      fetchDomains(); // Refresh the list
    } catch (error) {
      console.error('Failed to refresh WHOIS:', error);
      toast.error('Failed to refresh WHOIS data');
    } finally {
      setRefreshingId(null);
    }
  };

  const handleDeleteDomain = async (domainId, domainName) => {
    if (!window.confirm(`Are you sure you want to delete ${domainName}?`)) {
      return;
    }

    try {
      await domainAPI.deleteDomain(domainId);
      toast.success('Domain deleted successfully');
      fetchDomains(); // Refresh the list
    } catch (error) {
      console.error('Failed to delete domain:', error);
      toast.error('Failed to delete domain');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'expired':
        return 'bg-danger-100 text-danger-800';
      case 'critical':
        return 'bg-danger-100 text-danger-800';
      case 'warning':
        return 'bg-warning-100 text-warning-800';
      case 'active':
        return 'bg-success-100 text-success-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'expired':
        return <XCircleIcon className="h-4 w-4" />;
      case 'critical':
        return <ExclamationTriangleIcon className="h-4 w-4" />;
      case 'warning':
        return <ClockIcon className="h-4 w-4" />;
      case 'active':
        return <CheckCircleIcon className="h-4 w-4" />;
      default:
        return <ClockIcon className="h-4 w-4" />;
    }
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Domains</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage your domain portfolio and renewal settings
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <Link
            to="/add-domain"
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 sm:w-auto"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Domain
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search domains..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            />
          </div>
        </div>
        <div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
            <option value="expired">Expired</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      {/* Domains Table */}
      <div className="mt-8 flex flex-col">
        <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
              {loading ? (
                <div className="bg-white px-6 py-12 text-center">
                  <ArrowPathIcon className="mx-auto h-8 w-8 animate-spin text-primary-600" />
                  <p className="mt-2 text-sm text-gray-500">Loading domains...</p>
                </div>
              ) : domains.length === 0 ? (
                <div className="bg-white px-6 py-12 text-center">
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No domains found</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    {searchTerm || statusFilter 
                      ? 'Try adjusting your search or filter criteria.'
                      : 'Get started by adding your first domain.'
                    }
                  </p>
                  {!searchTerm && !statusFilter && (
                    <div className="mt-6">
                      <Link
                        to="/add-domain"
                        className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                      >
                        <PlusIcon className="h-4 w-4 mr-2" />
                        Add Domain
                      </Link>
                    </div>
                  )}
                </div>
              ) : (
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Domain
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Expiration
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Registrar
                      </th>
                      <th className="relative px-6 py-3">
                        <span className="sr-only">Actions</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {domains.map((domain) => (
                      <tr key={domain.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {domain.name}
                            </div>
                            {domain.notes && (
                              <div className="text-sm text-gray-500 truncate max-w-xs">
                                {domain.notes}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(domain.status)}`}>
                            {getStatusIcon(domain.status)}
                            <span className="ml-1 capitalize">{domain.status}</span>
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div>
                            <div className="font-medium">
                              {format(new Date(domain.expiration_date), 'MMM dd, yyyy')}
                            </div>
                            <div className="text-gray-500">
                              {domain.days_until_expiration <= 0 
                                ? 'Expired' 
                                : `${domain.days_until_expiration} days left`
                              }
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {domain.registrar || 'Unknown'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end space-x-2">
                            <button
                              onClick={() => handleRefreshWhois(domain.id)}
                              disabled={refreshingId === domain.id}
                              className="text-primary-600 hover:text-primary-900 disabled:opacity-50"
                              title="Refresh WHOIS data"
                            >
                              <ArrowPathIcon 
                                className={`h-4 w-4 ${refreshingId === domain.id ? 'animate-spin' : ''}`} 
                              />
                            </button>
                            <button
                              className="text-primary-600 hover:text-primary-900"
                              title="Edit domain"
                            >
                              <PencilIcon className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteDomain(domain.id, domain.name)}
                              className="text-danger-600 hover:text-danger-900"
                              title="Delete domain"
                            >
                              <TrashIcon className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Domains; 
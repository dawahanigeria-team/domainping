import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ExclamationTriangleIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlusIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { domainAPI } from '../services/api';
import { format, formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [expiringDomains, setExpiringDomains] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, expiringResponse] = await Promise.all([
        domainAPI.getStatistics(),
        domainAPI.getExpiringDomains(30) // Next 30 days
      ]);
      
      setStats(statsResponse.data);
      setExpiringDomains(expiringResponse.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'expired':
        return 'text-danger-600 bg-danger-50';
      case 'critical':
        return 'text-danger-600 bg-danger-50';
      case 'warning':
        return 'text-warning-600 bg-warning-50';
      case 'active':
        return 'text-success-600 bg-success-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'expired':
        return <XCircleIcon className="h-5 w-5" />;
      case 'critical':
        return <ExclamationTriangleIcon className="h-5 w-5" />;
      case 'warning':
        return <ClockIcon className="h-5 w-5" />;
      case 'active':
        return <CheckCircleIcon className="h-5 w-5" />;
      default:
        return <ClockIcon className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArrowPathIcon className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700">
            Overview of your domain portfolio and upcoming renewals
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

      {/* Stats Cards */}
      {stats && (
        <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-6 w-6 text-success-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Domains
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.total_domains}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ExclamationTriangleIcon className="h-6 w-6 text-danger-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Critical (≤7 days)
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.critical_domains}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ClockIcon className="h-6 w-6 text-warning-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Warning (≤30 days)
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.warning_domains}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <XCircleIcon className="h-6 w-6 text-danger-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Expired
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.expired_domains}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Expiring Domains */}
      <div className="mt-8">
        <div className="sm:flex sm:items-center">
          <div className="sm:flex-auto">
            <h2 className="text-lg font-medium text-gray-900">
              Domains Expiring Soon
            </h2>
            <p className="mt-1 text-sm text-gray-700">
              Domains expiring in the next 30 days
            </p>
          </div>
          <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
            <Link
              to="/domains"
              className="text-sm font-medium text-primary-600 hover:text-primary-500"
            >
              View all domains →
            </Link>
          </div>
        </div>

        <div className="mt-4 bg-white shadow overflow-hidden sm:rounded-md">
          {expiringDomains.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircleIcon className="mx-auto h-12 w-12 text-success-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                No domains expiring soon
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                All your domains are safe for the next 30 days!
              </p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {expiringDomains.slice(0, 10).map((domain) => (
                <li key={domain.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className={`flex-shrink-0 p-2 rounded-full ${getStatusColor(domain.status)}`}>
                          {getStatusIcon(domain.status)}
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-900">
                            {domain.name}
                          </p>
                          <p className="text-sm text-gray-500">
                            {domain.registrar && `Registered with ${domain.registrar}`}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          {format(new Date(domain.expiration_date), 'MMM dd, yyyy')}
                        </p>
                        <p className="text-sm text-gray-500">
                          {domain.days_until_expiration <= 0 
                            ? 'Expired' 
                            : `${domain.days_until_expiration} days left`
                          }
                        </p>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 
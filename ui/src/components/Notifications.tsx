import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  title?: string;
  timestamp: Date;
  autoDismiss?: boolean;
  duration?: number;
}

interface NotificationsProps {
  notifications: Notification[];
  onDismiss: (id: string) => void;
}

const iconMap = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const colorMap = {
  success: 'bg-green-500 dark:bg-green-600',
  error: 'bg-red-500 dark:bg-red-600',
  warning: 'bg-yellow-500 dark:bg-yellow-600',
  info: 'bg-blue-500 dark:bg-blue-600',
};

const borderColorMap = {
  success: 'border-green-500 dark:border-green-600',
  error: 'border-red-500 dark:border-red-600',
  warning: 'border-yellow-500 dark:border-yellow-600',
  info: 'border-blue-500 dark:border-blue-600',
};

export const Notifications: React.FC<NotificationsProps> = ({ notifications, onDismiss }) => {
  const [visible, setVisible] = useState<Set<string>>(new Set(notifications.map(n => n.id)));

  useEffect(() => {
    notifications.forEach(notification => {
      if (notification.autoDismiss !== false) {
        const duration = notification.duration || 5000;
        const timer = setTimeout(() => {
          setVisible(prev => {
            const next = new Set(prev);
            next.delete(notification.id);
            return next;
          });
          setTimeout(() => onDismiss(notification.id), 300);
        }, duration);
        return () => clearTimeout(timer);
      }
    });
  }, [notifications, onDismiss]);

  const handleDismiss = (id: string) => {
    setVisible(prev => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
    setTimeout(() => onDismiss(id), 300);
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
      {notifications.map(notification => {
        const Icon = iconMap[notification.type];
        const isVisible = visible.has(notification.id);
        
        return (
          <div
            key={notification.id}
            className={`
              transform transition-all duration-300 ease-in-out
              ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
              bg-white dark:bg-gray-800 rounded-lg shadow-lg border-l-4
              ${borderColorMap[notification.type]} p-4 flex items-start space-x-3
            `}
          >
            <div className={`flex-shrink-0 ${colorMap[notification.type]} rounded-full p-1`}>
              <Icon className="w-5 h-5 text-white" />
            </div>
            
            <div className="flex-1 min-w-0">
              {notification.title && (
                <p className="text-sm font-semibold text-gray-900 dark:text-white">
                  {notification.title}
                </p>
              )}
              <p className="text-sm text-gray-700 dark:text-gray-300">
                {notification.message}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {notification.timestamp.toLocaleTimeString()}
              </p>
            </div>
            
            <button
              onClick={() => handleDismiss(notification.id)}
              className="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
              aria-label="Dismiss notification"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        );
      })}
    </div>
  );
};

export const NotificationCenter: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `notif-${Date.now()}-${Math.random()}`,
      timestamp: new Date(),
    };
    setNotifications(prev => [newNotification, ...prev]);
  };

  const dismissNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  return (
    <>
      <Notifications notifications={notifications} onDismiss={dismissNotification} />
      
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="relative p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          aria-label="Open notification center"
        >
          <AlertCircle className="w-6 h-6" />
          {notifications.length > 0 && (
            <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {notifications.length}
            </span>
          )}
        </button>
        
        {isOpen && (
          <div className="absolute right-0 mt-2 w-96 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 max-h-96 overflow-y-auto">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Notifications
              </h3>
              <button
                onClick={clearAll}
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                Clear all
              </button>
            </div>
            
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                  No notifications
                </div>
              ) : (
                notifications.map(notification => (
                  <div key={notification.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                    <div className="flex items-start space-x-3">
                      <div className={`flex-shrink-0 ${colorMap[notification.type]} rounded-full p-1`}>
                        {React.createElement(iconMap[notification.type], { className: "w-4 h-4 text-white" })}
                      </div>
                      <div className="flex-1 min-w-0">
                        {notification.title && (
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {notification.title}
                          </p>
                        )}
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {notification.timestamp.toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Notifications;

import { useState } from 'react';
import {
  Bell,
  Clock,
  Apple,
  BarChart3,
  Target,
  CheckCircle,
  X,
  AlertCircle,
  TrendingUp,
  Trash2
} from 'lucide-react';

const NotificationsPanel = ({ isOpen, onClose, user }) => {
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: 'meal_reminder',
      title: 'Lunch Reminder',
      message: 'Time for your planned grilled chicken salad!',
      time: '2 minutes ago',
      isRead: false,
      icon: Clock,
      color: 'orange'
    },
    {
      id: 2,
      type: 'nutrition_summary',
      title: 'Daily Nutrition Update',
      message: 'You\'ve reached 62% of your calorie goal. Great progress!',
      time: '1 hour ago',
      isRead: false,
      icon: BarChart3,
      color: 'green'
    },
    {
      id: 3,
      type: 'nutrient_alert',
      title: 'Daily Nutrition Update',
      message: 'You\'ve reached 62% of your calorie goal. Great progress!',
      time: '1 hour ago',
      isRead: false,
      icon: BarChart3,
      color: 'green'
    },
     {
      id: 4,
      type: 'achievement',
      title: 'Streak Achievement! 🎉',
      message: 'Congratulations! 7-day meal logging streak maintained',
      time: '1 day ago',
      isRead: true,
      icon: TrendingUp,
      color: 'purple'
    },
    {
      id: 5,
      type: 'recipe_suggestion',
      title: 'New Recipe Match',
      message: 'AI found 3 recipes perfect for your fitness goals',
      time: '2 days ago',
      isRead: true,
      icon: Apple,
      color: 'cyan'
    }
  ]);

  const markAsRead = (notificationId) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === notificationId
          ? { ...notif, isRead: true }
          : notif
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notif => ({ ...notif, isRead: true }))
    );
  };

  const deleteNotification = (notificationId) => {
    setNotifications(prev =>
      prev.filter(notif => notif.id !== notificationId)
    );
    // TODO: Send to API endpoint
    // await apiService.deleteNotification({ userId, notificationId });
    console.log('Deleting notification:', notificationId);
  };

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const colorMap = {
    green: { bg: '#f0fdf4', border: '#bbf7d0', text: '#16a34a' },
    orange: { bg: '#fff7ed', border: '#fed7aa', text: '#ea580c' },
    yellow: { bg: '#fefce8', border: '#fef3c7', text: '#d97706' },
    cyan: { bg: '#ecfeff', border: '#a5f3fc', text: '#0891b2' },
    purple: { bg: '#faf5ff', border: '#e9d5ff', text: '#9333ea' }
  };

  return (
    <>
      {/* Backdrop overlay - only render when open */}
      {isOpen && (
        <div
          onClick={onClose}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: 'rgba(0, 0, 0, 0.3)',
            zIndex: 999,
            opacity: 1,
            transition: 'opacity 0.3s ease'
          }}
        />
      )}

      {/* Notification Panel */}
      <div style={{
        position: 'fixed',
        top: 0,
        right: 0,
        width: '400px',
        height: '100vh',
        background: '#ffffff',
        boxShadow: '-4px 0 12px -2px rgb(0 0 0 / 0.1)',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        borderLeft: '1px solid #f3f4f6',
        transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        visibility: isOpen ? 'visible' : 'hidden',
        pointerEvents: isOpen ? 'auto' : 'none'
      }}>
      {/* Header */}
      <div style={{
        padding: '24px',
        borderBottom: '1px solid #f3f4f6',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: 32,
            height: 32,
            background: '#f0fdf4',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Bell width={18} height={18} color="#22c55e" />
          </div>
          <div>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              margin: 0
            }}>
              Notifications
            </h2>
            {unreadCount > 0 && (
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: '2px 0 0 0'
              }}>
                {unreadCount} unread
              </p>
            )}
          </div>
        </div>
        <button
          onClick={onClose}
          style={{
            padding: '8px',
            background: 'transparent',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            color: '#6b7280',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => {
            e.target.style.background = '#f3f4f6';
          }}
          onMouseOut={(e) => {
            e.target.style.background = 'transparent';
          }}
        >
          <X width={20} height={20} />
        </button>
      </div>

      {/* Mark all as read button */}
      {unreadCount > 0 && (
        <div style={{ padding: '16px 24px 0 24px' }}>
          <button
            onClick={markAllAsRead}
            style={{
              fontSize: '14px',
              color: '#22c55e',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            Mark all as read
          </button>
        </div>
      )}

      {/* Notifications List */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px 0'
      }}>
        {notifications.map((notification) => {
          const colors = colorMap[notification.color] || colorMap.green;
          const IconComponent = notification.icon;

          return (
            <div
              key={notification.id}
              style={{
                padding: '16px 24px',
                borderLeft: !notification.isRead ? `3px solid ${colors.text}` : '3px solid transparent',
                background: !notification.isRead ? '#fafafa' : 'transparent',
                transition: 'all 0.2s',
                borderBottom: '1px solid #f9fafb',
                position: 'relative'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = '#f9fafb';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = !notification.isRead ? '#fafafa' : 'transparent';
              }}
            >
              <div style={{ display: 'flex', gap: '12px' }}>
                <div
                  onClick={() => markAsRead(notification.id)}
                  style={{
                    width: 40,
                    height: 40,
                    background: colors.bg,
                    borderRadius: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    border: `1px solid ${colors.border}`,
                    cursor: 'pointer'
                  }}
                >
                  <IconComponent width={20} height={20} color={colors.text} />
                </div>

                <div
                  onClick={() => markAsRead(notification.id)}
                  style={{ flex: 1, minWidth: 0, cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <h4 style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#111827',
                      margin: 0,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      flex: 1
                    }}>
                      {notification.title}
                    </h4>
                    {!notification.isRead && (
                      <div style={{
                        width: 8,
                        height: 8,
                        background: colors.text,
                        borderRadius: '50%',
                        flexShrink: 0
                      }} />
                    )}
                  </div>

                  <p style={{
                    fontSize: '13px',
                    color: '#6b7280',
                    margin: '0 0 8px 0',
                    lineHeight: '1.4'
                  }}>
                    {notification.message}
                  </p>

                  <p style={{
                    fontSize: '12px',
                    color: '#9ca3af',
                    margin: 0,
                    fontWeight: '500'
                  }}>
                    {notification.time}
                  </p>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteNotification(notification.id);
                  }}
                  style={{
                    padding: '8px',
                    background: 'transparent',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    color: '#9ca3af',
                    transition: 'all 0.2s',
                    alignSelf: 'flex-start'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.background = '#fee2e2';
                    e.currentTarget.style.color = '#ef4444';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.color = '#9ca3af';
                  }}
                >
                  <Trash2 width={16} height={16} />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div style={{
        padding: '16px 24px',
        borderTop: '1px solid #f3f4f6',
        background: '#f9fafb'
      }}>
        <button style={{
          width: '100%',
          padding: '12px',
          background: '#22c55e',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: '600',
          cursor: 'pointer',
          transition: 'all 0.2s'
        }}
        onMouseOver={(e) => {
          e.target.style.background = '#16a34a';
        }}
        onMouseOut={(e) => {
          e.target.style.background = '#22c55e';
        }}
        >
          View All Notifications
        </button>
      </div>
    </div>
    </>
  );
};

// Updated Bell Button Component
const NotificationBellButton = ({ unreadCount, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        position: 'relative',
        padding: '8px',
        color: '#6b7280',
        background: isHovered ? '#f3f4f6' : 'transparent',
        border: 'none',
        borderRadius: '8px',
        cursor: 'pointer',
        transition: 'all 0.2s'
      }}
    >
      <Bell width={20} height={20} />
      {unreadCount > 0 && (
        <div style={{
          position: 'absolute',
          top: '4px',
          right: '4px',
          width: '16px',
          height: '16px',
          background: '#ef4444',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '10px',
          fontWeight: '600',
          color: 'white',
          border: '2px solid white'
        }}>
          {unreadCount > 9 ? '9+' : unreadCount}
        </div>
      )}
    </button>
  );
};

export { NotificationsPanel, NotificationBellButton };

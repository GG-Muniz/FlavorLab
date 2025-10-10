import { X, TrendingUp, Target, Flame, Clock, Calendar } from 'lucide-react';

const CalorieDetailModal = ({ isOpen, onClose, calorieData }) => {
  if (!isOpen) return null;

  const { current, target, percentage } = calorieData;
  const remaining = target - current;
  const averagePerMeal = Math.round(remaining / 3); // Assuming 3 meals left

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'rgba(0, 0, 0, 0.5)',
          zIndex: 1001,
          opacity: isOpen ? 1 : 0,
          transition: 'opacity 0.3s ease',
          backdropFilter: 'blur(4px)'
        }}
      />

      {/* Modal */}
      <div style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: isOpen ? 'translate(-50%, -50%) scale(1)' : 'translate(-50%, -50%) scale(0.9)',
        width: '90%',
        maxWidth: '500px',
        background: '#ffffff',
        borderRadius: '24px',
        boxShadow: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        zIndex: 1002,
        opacity: isOpen ? 1 : 0,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        overflow: 'hidden'
      }}>
        {/* Header with gradient */}
        <div style={{
          background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
          padding: '32px 24px',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Decorative circles */}
          <div style={{
            position: 'absolute',
            top: '-40px',
            right: '-40px',
            width: '120px',
            height: '120px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '50%'
          }} />
          <div style={{
            position: 'absolute',
            bottom: '-20px',
            left: '-20px',
            width: '80px',
            height: '80px',
            background: 'rgba(255, 255, 255, 0.08)',
            borderRadius: '50%'
          }} />

          {/* Close button */}
          <button
            onClick={onClose}
            style={{
              position: 'absolute',
              top: '16px',
              right: '16px',
              background: 'rgba(255, 255, 255, 0.2)',
              border: 'none',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s',
              zIndex: 1
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
              e.currentTarget.style.transform = 'scale(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            <X width={18} height={18} color="#ffffff" />
          </button>

          <div style={{ position: 'relative', zIndex: 1 }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#ffffff',
              margin: '0 0 8px 0'
            }}>
              Calorie Progress
            </h2>
            <p style={{
              fontSize: '14px',
              color: 'rgba(255, 255, 255, 0.9)',
              margin: 0
            }}>
              Daily nutrition tracking summary
            </p>
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: '24px' }}>
          {/* Main Stats */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
            marginBottom: '24px'
          }}>
            {/* Current Intake */}
            <div style={{
              padding: '20px',
              background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
              borderRadius: '16px',
              border: '1px solid #bbf7d0'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '12px'
              }}>
                <Flame width={18} height={18} color="#16a34a" />
                <span style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#16a34a',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Consumed
                </span>
              </div>
              <p style={{
                fontSize: '32px',
                fontWeight: '800',
                color: '#111827',
                margin: '0 0 4px 0'
              }}>
                {current}
              </p>
              <p style={{
                fontSize: '13px',
                color: '#6b7280',
                margin: 0
              }}>
                kcal today
              </p>
            </div>

            {/* Remaining */}
            <div style={{
              padding: '20px',
              background: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)',
              borderRadius: '16px',
              border: '1px solid #fed7aa'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '12px'
              }}>
                <Target width={18} height={18} color="#ea580c" />
                <span style={{
                  fontSize: '12px',
                  fontWeight: '600',
                  color: '#ea580c',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Remaining
                </span>
              </div>
              <p style={{
                fontSize: '32px',
                fontWeight: '800',
                color: '#111827',
                margin: '0 0 4px 0'
              }}>
                {remaining}
              </p>
              <p style={{
                fontSize: '13px',
                color: '#6b7280',
                margin: 0
              }}>
                kcal left
              </p>
            </div>
          </div>

          {/* Progress Bar */}
          <div style={{ marginBottom: '24px' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '8px'
            }}>
              <span style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151'
              }}>
                Daily Goal Progress
              </span>
              <span style={{
                fontSize: '14px',
                fontWeight: '700',
                color: '#22c55e'
              }}>
                {percentage}%
              </span>
            </div>
            <div style={{
              width: '100%',
              height: '12px',
              background: '#f3f4f6',
              borderRadius: '999px',
              overflow: 'hidden',
              position: 'relative'
            }}>
              <div style={{
                height: '100%',
                width: `${percentage}%`,
                background: 'linear-gradient(90deg, #22c55e 0%, #16a34a 100%)',
                borderRadius: '999px',
                transition: 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
                boxShadow: '0 2px 8px rgba(34, 197, 94, 0.4)'
              }} />
            </div>
          </div>

          {/* Insights */}
          <div style={{
            padding: '20px',
            background: '#f9fafb',
            borderRadius: '16px',
            border: '1px solid #f3f4f6'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '16px'
            }}>
              <TrendingUp width={18} height={18} color="#22c55e" />
              <h3 style={{
                fontSize: '14px',
                fontWeight: '700',
                color: '#111827',
                margin: 0
              }}>
                Quick Insights
              </h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'start', gap: '10px' }}>
                <div style={{
                  width: '6px',
                  height: '6px',
                  background: '#22c55e',
                  borderRadius: '50%',
                  marginTop: '6px',
                  flexShrink: 0
                }} />
                <p style={{
                  fontSize: '13px',
                  color: '#6b7280',
                  margin: 0,
                  lineHeight: '1.5'
                }}>
                  You're <strong style={{ color: '#111827' }}>{percentage}%</strong> toward your daily goal
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'start', gap: '10px' }}>
                <div style={{
                  width: '6px',
                  height: '6px',
                  background: '#22c55e',
                  borderRadius: '50%',
                  marginTop: '6px',
                  flexShrink: 0
                }} />
                <p style={{
                  fontSize: '13px',
                  color: '#6b7280',
                  margin: 0,
                  lineHeight: '1.5'
                }}>
                  Average <strong style={{ color: '#111827' }}>{averagePerMeal} kcal</strong> per remaining meal
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'start', gap: '10px' }}>
                <div style={{
                  width: '6px',
                  height: '6px',
                  background: '#22c55e',
                  borderRadius: '50%',
                  marginTop: '6px',
                  flexShrink: 0
                }} />
                <p style={{
                  fontSize: '13px',
                  color: '#6b7280',
                  margin: 0,
                  lineHeight: '1.5'
                }}>
                  {percentage >= 75 ? 'Great progress! Stay on track.' : 'Keep going! You can do it.'}
                </p>
              </div>
            </div>
          </div>

          {/* Action Button */}
          <button
            onClick={onClose}
            style={{
              width: '100%',
              marginTop: '20px',
              padding: '14px',
              background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '12px',
              fontSize: '15px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: '0 4px 12px rgba(34, 197, 94, 0.3)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 16px rgba(34, 197, 94, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(34, 197, 94, 0.3)';
            }}
          >
            Got it
          </button>
        </div>
      </div>
    </>
  );
};

export default CalorieDetailModal;

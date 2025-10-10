import { useState } from 'react';
import { X, Calculator, Target, Flame, TrendingUp, Plus, ChevronDown } from 'lucide-react';

const CalorieCounter = ({ isOpen, onClose }) => {
  const [calorieGoal, setCalorieGoal] = useState('');
  const [calorieIntake, setCalorieIntake] = useState('');
  const [mealName, setMealName] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [savedGoal, setSavedGoal] = useState(null);
  const [intakeHistory, setIntakeHistory] = useState([]);

  const mealOptions = ['Breakfast', 'Lunch', 'Dinner', 'Snack'];

  if (!isOpen) return null;

  const handleSaveGoal = () => {
    if (calorieGoal && !isNaN(calorieGoal)) {
      setSavedGoal(Number(calorieGoal));
      // TODO: Send to API endpoint
      // await apiService.saveCalorieGoal({ userId, goal: calorieGoal });
      console.log('Saving calorie goal:', calorieGoal);
    }
  };

  const handleSelectMeal = (meal) => {
    setMealName(meal);
    setIsDropdownOpen(false);
  };

  const handleAddIntake = () => {
    if (calorieIntake && !isNaN(calorieIntake) && mealName.trim()) {
      const newIntake = {
        id: Date.now(),
        meal: mealName,
        calories: Number(calorieIntake),
        timestamp: new Date().toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit'
        })
      };
      setIntakeHistory([...intakeHistory, newIntake]);
      // TODO: Send to API endpoint
      // await apiService.logCalorieIntake({ userId, intake: newIntake });
      console.log('Adding calorie intake:', newIntake);

      // Reset inputs
      setCalorieIntake('');
      setMealName('');
    }
  };

  const totalIntake = intakeHistory.reduce((sum, item) => sum + item.calories, 0);
  const remaining = savedGoal ? savedGoal - totalIntake : null;
  const percentage = savedGoal ? Math.min(Math.round((totalIntake / savedGoal) * 100), 100) : 0;

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
        maxWidth: '600px',
        maxHeight: '90vh',
        background: '#ffffff',
        borderRadius: '24px',
        boxShadow: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        zIndex: 1002,
        opacity: isOpen ? 1 : 0,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
          padding: '32px 24px',
          position: 'relative',
          borderTopLeftRadius: '24px',
          borderTopRightRadius: '24px'
        }}>
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
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
            }}
          >
            <X width={18} height={18} color="#ffffff" />
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Calculator width={24} height={24} color="#ffffff" />
            </div>
            <div>
              <h2 style={{
                fontSize: '24px',
                fontWeight: '700',
                color: '#ffffff',
                margin: 0
              }}>
                Calorie Counter
              </h2>
              <p style={{
                fontSize: '14px',
                color: 'rgba(255, 255, 255, 0.9)',
                margin: '4px 0 0 0'
              }}>
                Track your daily calorie intake
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div style={{
          flex: 1,
          padding: '24px',
          borderBottomLeftRadius: '24px',
          borderBottomRightRadius: '24px',
          overflowY: 'auto'
        }}>
          {/* Progress Summary */}
          {savedGoal && (
            <div style={{
              padding: '20px',
              background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
              borderRadius: '16px',
              border: '1px solid #bbf7d0',
              marginBottom: '24px'
            }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr 1fr',
                gap: '16px',
                marginBottom: '16px'
              }}>
                <div>
                  <p style={{
                    fontSize: '12px',
                    fontWeight: '600',
                    color: '#6b7280',
                    margin: '0 0 4px 0',
                    textTransform: 'uppercase'
                  }}>
                    Goal
                  </p>
                  <p style={{
                    fontSize: '20px',
                    fontWeight: '700',
                    color: '#111827',
                    margin: 0
                  }}>
                    {savedGoal}
                  </p>
                </div>
                <div>
                  <p style={{
                    fontSize: '12px',
                    fontWeight: '600',
                    color: '#6b7280',
                    margin: '0 0 4px 0',
                    textTransform: 'uppercase'
                  }}>
                    Intake
                  </p>
                  <p style={{
                    fontSize: '20px',
                    fontWeight: '700',
                    color: '#111827',
                    margin: 0
                  }}>
                    {totalIntake}
                  </p>
                </div>
                <div>
                  <p style={{
                    fontSize: '12px',
                    fontWeight: '600',
                    color: '#6b7280',
                    margin: '0 0 4px 0',
                    textTransform: 'uppercase'
                  }}>
                    Remaining
                  </p>
                  <p style={{
                    fontSize: '20px',
                    fontWeight: '700',
                    color: remaining >= 0 ? '#22c55e' : '#ef4444',
                    margin: 0
                  }}>
                    {remaining}
                  </p>
                </div>
              </div>

              {/* Progress Bar */}
              <div style={{
                width: '100%',
                height: '8px',
                background: '#ffffff',
                borderRadius: '999px',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${percentage}%`,
                  background: percentage > 100
                    ? 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)'
                    : 'linear-gradient(90deg, #22c55e 0%, #16a34a 100%)',
                  borderRadius: '999px',
                  transition: 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
                }} />
              </div>
            </div>
          )}

          {/* Set Calorie Goal Section */}
          <div style={{ marginBottom: '24px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '12px'
            }}>
              <Target width={18} height={18} color="#22c55e" />
              <h3 style={{
                fontSize: '16px',
                fontWeight: '700',
                color: '#111827',
                margin: 0
              }}>
                Daily Calorie Goal
              </h3>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <input
                type="number"
                value={calorieGoal}
                onChange={(e) => setCalorieGoal(e.target.value)}
                placeholder="Enter your daily goal"
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  borderRadius: '12px',
                  border: '2px solid #e5e7eb',
                  fontSize: '14px',
                  color: '#111827',
                  outline: 'none',
                  transition: 'all 0.2s'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#22c55e';
                  e.target.style.boxShadow = '0 0 0 3px rgba(34, 197, 94, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#e5e7eb';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <button
                onClick={handleSaveGoal}
                style={{
                  padding: '12px 24px',
                  background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(34, 197, 94, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                Set Goal
              </button>
            </div>
          </div>

          {/* Add Calorie Intake Section */}
          <div style={{ marginBottom: isDropdownOpen ? '200px' : '24px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '12px'
            }}>
              <Flame width={18} height={18} color="#ea580c" />
              <h3 style={{
                fontSize: '16px',
                fontWeight: '700',
                color: '#111827',
                margin: 0
              }}>
                Log Calorie Intake
              </h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {/* Custom Dropdown */}
              <div style={{ position: 'relative', zIndex: 100 }}>
                <button
                  type="button"
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '12px',
                    border: '2px solid #e5e7eb',
                    fontSize: '14px',
                    color: mealName ? '#111827' : '#9ca3af',
                    background: '#ffffff',
                    outline: 'none',
                    transition: 'all 0.2s',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => {
                    if (!isDropdownOpen) {
                      e.currentTarget.style.borderColor = '#22c55e';
                      e.currentTarget.style.boxShadow = '0 0 0 3px rgba(34, 197, 94, 0.1)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isDropdownOpen) {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }
                  }}
                >
                  <span>{mealName || 'Select meal type'}</span>
                  <ChevronDown
                    width={18}
                    height={18}
                    style={{
                      transition: 'transform 0.3s ease',
                      transform: isDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)'
                    }}
                  />
                </button>

                {/* Dropdown Menu */}
                <div style={{
                  position: 'absolute',
                  top: 'calc(100% + 4px)',
                  left: 0,
                  right: 0,
                  background: '#ffffff',
                  border: '2px solid #e5e7eb',
                  borderRadius: '12px',
                  boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
                  zIndex: 9999,
                  opacity: isDropdownOpen ? 1 : 0,
                  visibility: isDropdownOpen ? 'visible' : 'hidden',
                  transform: isDropdownOpen ? 'translateY(0)' : 'translateY(-10px)',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                }}>
                  {mealOptions.map((meal, index) => (
                    <button
                      key={meal}
                      type="button"
                      onClick={() => handleSelectMeal(meal)}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: 'none',
                        background: 'transparent',
                        fontSize: '14px',
                        color: '#111827',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'all 0.2s',
                        borderBottom: index < mealOptions.length - 1 ? '1px solid #f3f4f6' : 'none'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#f0fdf4';
                        e.currentTarget.style.color = '#16a34a';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'transparent';
                        e.currentTarget.style.color = '#111827';
                      }}
                    >
                      {meal}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px' }}>
                <input
                  type="number"
                  value={calorieIntake}
                  onChange={(e) => setCalorieIntake(e.target.value)}
                  placeholder="Calories consumed"
                  style={{
                    flex: 1,
                    padding: '12px 16px',
                    borderRadius: '12px',
                    border: '2px solid #e5e7eb',
                    fontSize: '14px',
                    color: '#111827',
                    outline: 'none',
                    transition: 'all 0.2s'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#22c55e';
                    e.target.style.boxShadow = '0 0 0 3px rgba(34, 197, 94, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#e5e7eb';
                    e.target.style.boxShadow = 'none';
                  }}
                />
                <button
                  onClick={handleAddIntake}
                  style={{
                    padding: '12px 24px',
                    background: 'linear-gradient(135deg, #ea580c 0%, #c2410c 100%)',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(234, 88, 12, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <Plus width={16} height={16} />
                  Add
                </button>
              </div>
            </div>
          </div>

          {/* Intake History */}
          {intakeHistory.length > 0 && (
            <div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '12px'
              }}>
                <TrendingUp width={18} height={18} color="#8b5cf6" />
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '700',
                  color: '#111827',
                  margin: 0
                }}>
                  Today's Intake
                </h3>
              </div>

              <div style={{
                background: '#f9fafb',
                borderRadius: '12px',
                border: '1px solid #f3f4f6',
                overflow: 'hidden'
              }}>
                {intakeHistory.map((item, index) => (
                  <div
                    key={item.id}
                    style={{
                      padding: '16px',
                      borderBottom: index < intakeHistory.length - 1 ? '1px solid #f3f4f6' : 'none',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <p style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#111827',
                        margin: '0 0 4px 0'
                      }}>
                        {item.meal}
                      </p>
                      <p style={{
                        fontSize: '12px',
                        color: '#6b7280',
                        margin: 0
                      }}>
                        {item.timestamp}
                      </p>
                    </div>
                    <div style={{
                      padding: '6px 12px',
                      background: '#f0fdf4',
                      borderRadius: '8px',
                      border: '1px solid #bbf7d0'
                    }}>
                      <p style={{
                        fontSize: '14px',
                        fontWeight: '700',
                        color: '#16a34a',
                        margin: 0
                      }}>
                        {item.calories} cal
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default CalorieCounter;

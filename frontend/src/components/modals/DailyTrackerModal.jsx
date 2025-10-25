import { useState, useEffect, useCallback, useMemo } from 'react';
import { X, Calculator, Target, Flame, TrendingUp, Plus, ChevronDown, Utensils, Edit, Trash2 } from 'lucide-react';
import { useData } from '../../context/DataContext.jsx';

const DailyTrackerModal = ({ isOpen, onClose }) => {
  // Get centralized data from DataContext (includes summary)
  const { loggedMeals, mealPlans, summary, isLoading, addLog, updateLog, deleteLog, logMeal, setGoal } = useData();

  // Only keep input form state local
  const [goalInput, setGoalInput] = useState('');
  const [calorieInput, setCalorieInput] = useState('');
  const [mealName, setMealName] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Tab state
  const [activeTab, setActiveTab] = useState('log-intake');

  // Success message state
  const [successMessage, setSuccessMessage] = useState('');

  // Edit state
  const [editingMeal, setEditingMeal] = useState(null);
  const [editCalories, setEditCalories] = useState('');
  const [editMealType, setEditMealType] = useState('');
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const mealOptions = ['Breakfast', 'Lunch', 'Dinner', 'Snack'];


  // ALL HOOKS MUST BE HERE, AT THE TOP LEVEL
  const handleLogMealPlan = useCallback(async (plan) => {
    await logMeal(plan.id);
    setSuccessMessage('Meal logged successfully!');
    setTimeout(() => setSuccessMessage(''), 3000);
  }, [logMeal]);

  const handleDeleteMeal = useCallback(async (mealId) => {
    if (!confirm('Are you sure you want to delete this meal?')) {
      return;
    }
    await deleteLog(mealId);
    setSuccessMessage('Meal deleted successfully!');
    setTimeout(() => setSuccessMessage(''), 3000);
  }, [deleteLog]);

  const handleEditMeal = useCallback((meal) => {
    setEditingMeal(meal);
    setEditCalories(meal.calories.toString());
    setEditMealType(meal.meal_type || 'Breakfast');
    setIsEditModalOpen(true);
  }, []);

  const handleUpdateMeal = useCallback(async () => {
    if (!editingMeal || !editCalories || !editMealType) {
      return;
    }

    const newCalories = parseInt(editCalories);

    // Guard Clause: Check if macro data exists and if calories are valid for scaling
    if (!editingMeal.protein || editingMeal.calories <= 0) {
      // This is a calorie-only log OR original calories are zero.
      // We can only update the calories.
      await updateLog(editingMeal.log_id, editMealType, newCalories);
    } else {
      // This is a full nutritional log. We must scale the macros.
      const ratio = newCalories / editingMeal.calories;
      const macroData = {
        protein: editingMeal.protein * ratio,
        carbs: editingMeal.carbs * ratio,
        fat: editingMeal.fat * ratio,
        fiber: editingMeal.fiber * ratio
      };
      await updateLog(editingMeal.log_id, editMealType, newCalories, macroData);
    }

    // Close edit modal
    setIsEditModalOpen(false);
    setEditingMeal(null);
    setEditCalories('');
    setEditMealType('');
  }, [editingMeal, editCalories, editMealType, updateLog]);

  const handleCancelEdit = useCallback(() => {
    setIsEditModalOpen(false);
    setEditingMeal(null);
    setEditCalories('');
    setEditMealType('');
  }, []);

  // --- END OF HOOKS SECTION ---

  // Create derived state for unlogged meal plans (action list behavior)
  const loggedMealKeys = useMemo(() => {
    // Create Set of unique keys for meals already logged today
    return new Set(loggedMeals.map(meal => `${meal.name}::${meal.meal_type}`));
  }, [loggedMeals]);

  const unloggedMealPlans = useMemo(() => {
    // Filter mealPlans to show only those not yet logged today
    return mealPlans.filter(plan => !loggedMealKeys.has(`${plan.name}::${plan.meal_type}`));
  }, [mealPlans, loggedMealKeys]);

  if (!isOpen) return null;

  const handleSaveGoal = async () => {
    if (goalInput && !isNaN(goalInput)) {
      try {
        // Call DataContext setGoal which handles API and refetch
        await setGoal(Number(goalInput));

        // Reset input
        setGoalInput('');
        console.log('Calorie goal saved successfully');
      } catch (err) {
        console.error('Error saving calorie goal:', err);
        alert('Failed to save calorie goal. Please try again.');
      }
    }
  };

  const handleSelectMeal = (meal) => {
    setMealName(meal);
    setIsDropdownOpen(false);
  };

  const handleAddIntake = async () => {
    if (calorieInput && !isNaN(calorieInput) && mealName.trim()) {
      await addLog(mealName, Number(calorieInput));
      setSuccessMessage('Meal logged successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);

      // Reset inputs
      setCalorieInput('');
      setMealName('');
    }
  };

  // Read all display values from context (with safety checks)
  const totalIntake = summary?.total_consumed || 0;
  const savedGoal = summary?.daily_goal || 0;
  const remaining = summary?.remaining || 0;
  const percentage = savedGoal > 0 ? Math.min(Math.round((totalIntake / savedGoal) * 100), 100) : 0;

  // Transform logged meals for display from DataContext
  const intakeHistory = loggedMeals.map((meal, index) => ({
    id: index,
    log_id: meal.log_id,
    meal: meal.name,
    calories: meal.calories,
    meal_type: meal.meal_type,
    timestamp: new Date(meal.logged_at).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    }),
    // Add the missing macro fields for proportional scaling
    protein: meal.protein || 0,
    carbs: meal.carbs || 0,
    fat: meal.fat || 0,
    fiber: meal.fiber || 0
  }));

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
          {/* Tab Navigation */}
          <div style={{
            display: 'flex',
            background: '#f8fafc',
            borderRadius: '12px',
            padding: '6px',
            marginBottom: '24px',
            border: '2px solid #e2e8f0',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <button
              onClick={() => setActiveTab('log-intake')}
              style={{
                flex: 1,
                padding: '12px 20px',
                borderRadius: '8px',
                border: 'none',
                background: activeTab === 'log-intake' ? '#ffffff' : 'transparent',
                color: activeTab === 'log-intake' ? '#1e293b' : '#64748b',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                boxShadow: activeTab === 'log-intake' ? '0 2px 4px rgba(0, 0, 0, 0.1)' : 'none',
                border: activeTab === 'log-intake' ? '1px solid #e2e8f0' : '1px solid transparent'
              }}
            >
              Log Intake
            </button>
            <button
              onClick={() => setActiveTab('meal-plans')}
              style={{
                flex: 1,
                padding: '12px 20px',
                borderRadius: '8px',
                border: 'none',
                background: activeTab === 'meal-plans' ? '#ffffff' : 'transparent',
                color: activeTab === 'meal-plans' ? '#1e293b' : '#64748b',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                boxShadow: activeTab === 'meal-plans' ? '0 2px 4px rgba(0, 0, 0, 0.1)' : 'none',
                border: activeTab === 'meal-plans' ? '1px solid #e2e8f0' : '1px solid transparent'
              }}
            >
              Meal Plans
            </button>
          </div>

          {/* Success Message */}
          {successMessage && (
            <div style={{
              padding: '12px 16px',
              background: '#f0fdf4',
              border: '1px solid #bbf7d0',
              borderRadius: '12px',
              marginBottom: '16px',
              color: '#166534',
              fontSize: '14px',
              fontWeight: '500'
            }}>
              {successMessage}
            </div>
          )}

          {/* Tab Content */}
          {activeTab === 'log-intake' && (
            <>
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
                value={goalInput}
                onChange={(e) => setGoalInput(e.target.value)}
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
                disabled={isLoading}
                style={{
                  padding: '12px 24px',
                  background: isLoading ? '#9ca3af' : 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s',
                  opacity: isLoading ? 0.7 : 1
                }}
                onMouseEnter={(e) => {
                  if (!isLoading) {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(34, 197, 94, 0.3)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isLoading) {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }
                }}
              >
                {isLoading ? 'Saving...' : 'Set Goal'}
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
                  value={calorieInput}
                  onChange={(e) => setCalorieInput(e.target.value)}
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
                  disabled={isLoading}
                  style={{
                    padding: '12px 24px',
                    background: isLoading ? '#9ca3af' : 'linear-gradient(135deg, #ea580c 0%, #c2410c 100%)',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: isLoading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    opacity: isLoading ? 0.7 : 1
                  }}
                  onMouseEnter={(e) => {
                    if (!isLoading) {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(234, 88, 12, 0.3)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isLoading) {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = 'none';
                    }
                  }}
                >
                  <Plus width={16} height={16} />
                  {isLoading ? 'Adding...' : 'Add'}
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
                    <div style={{ flex: 1 }}>
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
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
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
                      <div style={{
                        display: 'flex',
                        gap: '4px'
                      }}>
                        <button
                          onClick={() => handleEditMeal(item)}
                          style={{
                            padding: '6px',
                            background: '#f3f4f6',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'all 0.2s'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.background = '#e5e7eb';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background = '#f3f4f6';
                          }}
                        >
                          <Edit width={14} height={14} color="#6b7280" />
                        </button>
                        <button
                          onClick={() => handleDeleteMeal(item.log_id)}
                          style={{
                            padding: '6px',
                            background: '#fef2f2',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'all 0.2s'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.background = '#fee2e2';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background = '#fef2f2';
                          }}
                        >
                          <Trash2 width={14} height={14} color="#dc2626" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
            </>
          )}

          {/* Meal Plans Tab */}
          {activeTab === 'meal-plans' && (
            <div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '12px'
              }}>
                <Utensils width={18} height={18} color="#8b5cf6" />
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '700',
                  color: '#111827',
                  margin: 0
                }}>
                  Your Meal Plans
                </h3>
              </div>

              {isLoading ? (
                <div style={{
                  padding: '20px',
                  textAlign: 'center',
                  color: '#6b7280'
                }}>
                  Loading meal plans...
                </div>
              ) : unloggedMealPlans.length === 0 ? (
                <div style={{
                  padding: '32px 20px',
                  textAlign: 'center',
                  color: '#64748b',
                  background: '#ffffff',
                  borderRadius: '12px',
                  border: '2px solid #e2e8f0',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  <Utensils width={32} height={32} color="#cbd5e1" style={{ marginBottom: '12px' }} />
                  <p style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#475569',
                    margin: '0 0 8px 0'
                  }}>
                    No meal plans available
                  </p>
                  <p style={{
                    fontSize: '14px',
                    color: '#64748b',
                    margin: 0
                  }}>
                    Generate some meal plans first!
                  </p>
                </div>
              ) : (
                <div style={{
                  background: '#ffffff',
                  borderRadius: '12px',
                  border: '2px solid #e2e8f0',
                  overflow: 'hidden',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
                }}>
                  {unloggedMealPlans.map((plan, index) => (
                    <div
                      key={plan.id}
                      style={{
                        padding: '20px',
                        borderBottom: index < unloggedMealPlans.length - 1 ? '1px solid #f1f5f9' : 'none',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        gap: '16px'
                      }}
                    >
                      <div style={{ flex: 1, minWidth: 0 }}>
                        {/* Meal Name - Primary */}
                        <h4 style={{
                          fontSize: '16px',
                          fontWeight: '700',
                          color: '#1e293b',
                          margin: '0 0 8px 0',
                          lineHeight: '1.3'
                        }}>
                          {plan.name}
                        </h4>

                        {/* Meal Type & Calories - Secondary */}
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          marginBottom: '8px'
                        }}>
                          <span style={{
                            fontSize: '13px',
                            fontWeight: '600',
                            color: '#ea580c',
                            background: '#fef3c7',
                            padding: '2px 8px',
                            borderRadius: '6px',
                            textTransform: 'capitalize'
                          }}>
                            {plan.meal_type}
                          </span>
                          <span style={{
                            fontSize: '13px',
                            fontWeight: '600',
                            color: '#ea580c'
                          }}>
                            {plan.calories} cal
                          </span>
                        </div>

                        {/* Description - Tertiary */}
                        {plan.description && (
                          <p style={{
                            fontSize: '14px',
                            color: '#64748b',
                            margin: 0,
                            lineHeight: '1.4',
                            maxWidth: '100%'
                          }}>
                            {plan.description}
                          </p>
                        )}
                      </div>

                      {/* Log Button */}
                      <button
                        onClick={() => handleLogMealPlan(plan)}
                        disabled={isLoading}
                        style={{
                          padding: '10px 16px',
                          background: isLoading ? '#9ca3af' : '#ea580c',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '8px',
                          fontSize: '13px',
                          fontWeight: '600',
                          cursor: isLoading ? 'not-allowed' : 'pointer',
                          transition: 'all 0.2s',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          opacity: isLoading ? 0.7 : 1,
                          boxShadow: isLoading ? 'none' : '0 2px 4px rgba(234, 88, 12, 0.2)',
                          flexShrink: 0
                        }}
                        onMouseEnter={(e) => {
                          if (!isLoading) {
                            e.currentTarget.style.transform = 'translateY(-1px)';
                            e.currentTarget.style.boxShadow = '0 4px 8px rgba(234, 88, 12, 0.3)';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (!isLoading) {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = '0 2px 4px rgba(234, 88, 12, 0.2)';
                          }
                        }}
                      >
                        <Plus width={14} height={14} />
                        {isLoading ? 'Logging...' : 'Log'}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Edit Meal Modal */}
      {isEditModalOpen && (
        <>
          {/* Backdrop */}
          <div
            onClick={handleCancelEdit}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              background: 'rgba(0, 0, 0, 0.5)',
              zIndex: 2001,
              backdropFilter: 'blur(4px)'
            }}
          />

          {/* Edit Modal */}
          <div style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '90%',
            maxWidth: '400px',
            background: '#ffffff',
            borderRadius: '16px',
            boxShadow: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
            zIndex: 2002,
            padding: '24px'
          }}>
            <h3 style={{
              fontSize: '18px',
              fontWeight: '700',
              color: '#111827',
              margin: '0 0 16px 0'
            }}>
              Edit Meal
            </h3>

            <div style={{ marginBottom: '16px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '6px'
              }}>
                Meal Type
              </label>
              <select
                value={editMealType}
                onChange={(e) => setEditMealType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px',
                  background: '#ffffff'
                }}
              >
                {mealOptions.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                marginBottom: '6px'
              }}>
                Calories
              </label>
              <input
                type="number"
                value={editCalories}
                onChange={(e) => setEditCalories(e.target.value)}
                placeholder="Enter calories"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  fontSize: '14px'
                }}
              />
            </div>

            <div style={{
              display: 'flex',
              gap: '12px',
              justifyContent: 'flex-end'
            }}>
              <button
                onClick={handleCancelEdit}
                style={{
                  padding: '10px 20px',
                  background: '#f3f4f6',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#374151',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#e5e7eb';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#f3f4f6';
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateMeal}
                disabled={isLoading}
                style={{
                  padding: '10px 20px',
                  background: isLoading ? '#9ca3af' : '#8b5cf6',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#ffffff',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!isLoading) {
                    e.currentTarget.style.background = '#7c3aed';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isLoading) {
                    e.currentTarget.style.background = '#8b5cf6';
                  }
                }}
              >
                {isLoading ? 'Updating...' : 'Update Meal'}
              </button>
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default DailyTrackerModal;

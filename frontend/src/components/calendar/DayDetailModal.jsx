import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Calendar as CalendarIcon, TrendingUp, FileText, Edit3, Save, Trash2, Clock } from 'lucide-react';
import moment from 'moment';
import { useData } from '../../context/DataContext';

const DayDetailModal = ({ isOpen, onClose, selectedDate, dayData, isNew, onSave, onDelete, isLoading }) => {
  const { getJournalNote, saveJournalNote, deleteJournalNote } = useData();

  // Existing note state (for backward compatibility)
  const [note, setNote] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editedNote, setEditedNote] = useState('');

  // New journal state
  const [journalNote, setJournalNote] = useState('');
  const [isJournalEditing, setIsJournalEditing] = useState(false);
  const [journalLoading, setJournalLoading] = useState(false);
  const [journalError, setJournalError] = useState(null);

  // Tab and journal window state
  const [activeTab, setActiveTab] = useState('meals');
  const [showJournalWindow, setShowJournalWindow] = useState(false);

  // Load journal note when modal opens
  // IMPORTANT: This useEffect MUST be before the early return to comply with Rules of Hooks
  useEffect(() => {
    if (isOpen && selectedDate) {
      const dateKey = moment(selectedDate).format('YYYY-MM-DD');
      loadJournalNote(dateKey);
    }
  }, [isOpen, selectedDate]);

  // Load journal note for the selected date
  const loadJournalNote = async (dateKey) => {
    if (!selectedDate) return;

    setJournalLoading(true);
    setJournalError(null);

    try {
      const journalData = await getJournalNote(dateKey);
      if (journalData) {
        setJournalNote(journalData.note_text || '');
      } else {
        setJournalNote('');
      }
    } catch (error) {
      console.error('Error loading journal note:', error);
      setJournalError('Failed to load journal note');
    } finally {
      setJournalLoading(false);
    }
  };

  // Handle journal note save
  const handleJournalSave = async () => {
    if (!selectedDate || !journalNote.trim()) return;

    const dateKey = moment(selectedDate).format('YYYY-MM-DD');
    setJournalLoading(true);
    setJournalError(null);

    try {
      await saveJournalNote(dateKey, journalNote.trim());
      setIsJournalEditing(false);
    } catch (error) {
      console.error('Error saving journal note:', error);
      setJournalError('Failed to save journal note');
    } finally {
      setJournalLoading(false);
    }
  };

  // Handle journal note delete
  const handleJournalDelete = async () => {
    if (!selectedDate) return;

    const dateKey = moment(selectedDate).format('YYYY-MM-DD');
    setJournalLoading(true);
    setJournalError(null);

    try {
      await deleteJournalNote(dateKey);
      setJournalNote('');
      setIsJournalEditing(false);
    } catch (error) {
      console.error('Error deleting journal note:', error);
      setJournalError('Failed to delete journal note');
    } finally {
      setJournalLoading(false);
    }
  };

  // Handle journal edit start - open writing window
  const handleJournalEdit = () => {
    setShowJournalWindow(true);
    setIsJournalEditing(true);
  };

  // Handle journal edit cancel - close writing window
  const handleJournalCancel = () => {
    setShowJournalWindow(false);
    setIsJournalEditing(false);
    setJournalError(null);
  };

  // Handle journal save and close window
  const handleJournalSaveAndClose = async () => {
    await handleJournalSave();
    if (!journalError) {
      setShowJournalWindow(false);
    }
  };

  // Early return AFTER all hooks have been called
  if (!selectedDate) return null;

  // Format the date nicely
  const formattedDate = moment(selectedDate).format('dddd, MMMM D, YYYY');
  const dateKey = moment(selectedDate).format('YYYY-MM-DD');

  // Determine which state to render based on data structure
  const hasMealLog = dayData && dayData.totals;
  const hasNoteOnly = dayData && dayData.note && !dayData.totals;

  // NutritionTag component for displaying nutrition values as white cards
  const NutritionTag = ({ label, value, unit, icon, color }) => (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#ffffff',
      padding: '16px',
      borderRadius: '12px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      minWidth: '80px',
      flex: 1,
      gap: '8px'
    }}>
      <div style={{
        fontSize: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        background: `${color}15`
      }}>
        {icon}
      </div>
      <div style={{
        fontSize: '20px',
        fontWeight: '700',
        color: '#111827'
      }}>
        {value}
      </div>
      <div style={{
        fontSize: '12px',
        fontWeight: '500',
        color: '#6b7280',
        textAlign: 'center'
      }}>
        {label}
      </div>
    </div>
  );

  // MealTag component for displaying meals as chips
  const MealTag = ({ meal, mealType }) => (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      background: 'linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%)',
      color: '#374151',
      padding: '12px 16px',
      borderRadius: '10px',
      fontSize: '13px',
      fontWeight: '500',
      borderLeft: '3px solid #86efac',
      borderRight: '1px solid #d1fae5',
      borderTop: '1px solid #d1fae5',
      borderBottom: '1px solid #d1fae5',
      marginBottom: '8px',
      transition: 'all 0.2s',
      cursor: 'default'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.background = '#ecfdf5';
      e.currentTarget.style.transform = 'translateX(4px)';
      e.currentTarget.style.boxShadow = '0 2px 6px rgba(34, 197, 94, 0.1)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.background = 'linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%)';
      e.currentTarget.style.transform = 'translateX(0)';
      e.currentTarget.style.boxShadow = 'none';
    }}
    >
      <span style={{ fontSize: '12px', textTransform: 'capitalize', color: '#059669', fontWeight: '600' }}>{mealType}:</span>
      <span>{meal}</span>
    </div>
  );

  // Handle save note (for new days)
  const handleSaveNote = () => {
    if (!note.trim()) return;

    // Call the onSave prop with date and note data
    onSave(selectedDate, { note: note.trim() });

    // Log for debugging
    console.log(`ACTION: Save Note for ${dateKey}`);
    console.log('Note content:', note.trim());

    // Clear the note and close modal
    setNote('');
    onClose();
  };

  // Handle edit button click
  const handleEditClick = () => {
    setEditedNote(dayData.note); // Pre-fill with existing note
    setIsEditing(true);
  };

  // Handle save edited note
  const handleSaveEdit = () => {
    if (!editedNote.trim()) return;

    // Call the onSave prop with updated note
    onSave(selectedDate, { note: editedNote.trim() });

    // Log for debugging
    console.log(`ACTION: Update Note for ${dateKey}`);
    console.log('Updated note content:', editedNote.trim());

    // Exit edit mode
    setIsEditing(false);
    setEditedNote('');
  };

  // Handle cancel edit
  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedNote('');
  };

  // Handle view full log (for existing days)
  const handleViewFullLog = () => {
    console.log(`ACTION: Navigate to Meal History for ${dateKey}`);
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
          <motion.div
          key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(240, 253, 244, 0.7)',
              backdropFilter: 'blur(4px)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px'
            }}
          />
      )}
      {isOpen && (
        <motion.div
          key="modal"
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 1200,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '40px 20px',
            pointerEvents: 'none'
          }}
        >
          <div
            style={{
              width: '90%',
              maxWidth: '700px',
              maxHeight: '85vh',
              background: '#ffffff',
              borderRadius: '16px',
              boxShadow: '0 10px 25px rgba(0, 0, 0, 0.08), 0 4px 10px rgba(0, 0, 0, 0.05)',
              border: '1px solid #e5e7eb',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              pointerEvents: 'auto'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div style={{
              padding: '24px',
              background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
              borderBottom: '2px solid #d1fae5',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start'
            }}>
              <div>
                <h2 style={{
                  fontSize: '22px',
                  fontWeight: '700',
                  color: '#065f46',
                  margin: '0 0 8px 0'
                }}>
                  {hasMealLog ? 'Health Journal' : hasNoteOnly ? 'Your Note' : 'New Entry'}
                </h2>
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: '#ffffff',
                  padding: '4px 10px',
                  borderRadius: '8px',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#374151',
                  border: '1px solid #d1fae5'
                }}>
                  <CalendarIcon width={14} height={14} color="#6b7280" />
                  <span>{moment(selectedDate).format('MMM DD, YYYY')}</span>
                </div>
              </div>
              <button
                onClick={onClose}
                style={{
                  padding: '8px',
                  background: 'rgba(6, 95, 70, 0.1)',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(6, 95, 70, 0.2)';
                  e.currentTarget.style.transform = 'scale(1.05)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(6, 95, 70, 0.1)';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <X width={20} height={20} color="#065f46" />
              </button>
            </div>

            {/* Content - Three States */}
            <div style={{
              flex: 1,
              overflowY: 'auto',
              padding: '24px'
            }}>
              {isLoading ? (
                /* LOADING STATE */
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '48px 20px',
                  minHeight: '200px'
                }}>
                  <div style={{
                    width: '48px',
                    height: '48px',
                    border: '4px solid #f3f4f6',
                    borderTop: '4px solid #22c55e',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }} />
                  <style>
                    {`
                      @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                      }
                    `}
                  </style>
                  <p style={{
                    marginTop: '16px',
                    fontSize: '14px',
                    color: '#6b7280',
                    fontWeight: '500'
                  }}>
                    Loading meal data...
                  </p>
                </div>
              ) : hasMealLog ? (
                /* STATE 1: Meal Log Display - Show meal summary */
                <>
                  {/* Daily Totals Summary */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    style={{
                      marginBottom: '24px'
                    }}
                  >
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(5, 1fr)',
                      gap: '12px'
                    }}>
                      <NutritionTag
                        label="KCAL"
                        value={dayData.totals.calories}
                        unit=""
                        icon="🔥"
                        color="#f59e0b"
                      />
                      <NutritionTag
                        label="PROTEIN"
                        value={dayData.totals.protein}
                        unit="g"
                        icon="🥩"
                        color="#22c55e"
                      />
                      <NutritionTag
                        label="CARBS"
                        value={dayData.totals.carbs}
                        unit="g"
                        icon="🌾"
                        color="#fbbf24"
                      />
                      <NutritionTag
                        label="FAT"
                        value={dayData.totals.fat}
                        unit="g"
                        icon="💧"
                        color="#3b82f6"
                      />
                      <NutritionTag
                        label="FIBER"
                        value={dayData.totals.fiber}
                        unit="g"
                        icon="🌿"
                        color="#a855f7"
                      />
                    </div>
                  </motion.div>

                  {/* Tab Navigation */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                        <div style={{
                      display: 'flex',
                      gap: '4px',
                      marginBottom: '16px',
                      borderBottom: '1px solid #e5e7eb'
                    }}>
                      <button
                        onClick={() => setActiveTab('meals')}
                        style={{
                          padding: '8px 16px',
                          background: activeTab === 'meals' ? 'linear-gradient(135deg, #86efac 0%, #4ade80 100%)' : 'transparent',
                          border: 'none',
                          borderBottom: activeTab === 'meals' ? '2px solid #22c55e' : '2px solid transparent',
                          borderRadius: '8px 8px 0 0',
                            fontSize: '14px',
                            fontWeight: '600',
                          color: activeTab === 'meals' ? '#065f46' : '#6b7280',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          if (activeTab !== 'meals') {
                            e.currentTarget.style.background = '#f0fdf4';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (activeTab !== 'meals') {
                            e.currentTarget.style.background = 'transparent';
                          }
                        }}
                      >
                        Meals
                      </button>
                      <button
                        onClick={() => setActiveTab('journal')}
                        style={{
                          padding: '8px 16px',
                          background: activeTab === 'journal' ? 'linear-gradient(135deg, #86efac 0%, #4ade80 100%)' : 'transparent',
                          border: 'none',
                          borderBottom: activeTab === 'journal' ? '2px solid #22c55e' : '2px solid transparent',
                          borderRadius: '8px 8px 0 0',
                          fontSize: '14px',
                          fontWeight: '600',
                          color: activeTab === 'journal' ? '#065f46' : '#6b7280',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          if (activeTab !== 'journal') {
                            e.currentTarget.style.background = '#f0fdf4';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (activeTab !== 'journal') {
                            e.currentTarget.style.background = 'transparent';
                          }
                        }}
                      >
                        Journal
                      </button>
                        </div>

                    {/* Tab Content */}
                    {activeTab === 'meals' ? (
                        <>
                        {/* Full Log Preview Window */}
                        <div style={{
                          background: 'linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%)',
                          border: '1px solid #d1fae5',
                          borderRadius: '12px',
                          padding: '16px',
                          marginBottom: '16px'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                            <Clock width={16} height={16} color="#059669" />
                            <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#065f46', margin: 0 }}>
                              Full Day Summary
                            </h4>
                          </div>
                          <div style={{
                            background: '#ffffff',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            padding: '12px',
                            fontSize: '12px',
                            lineHeight: '1.6',
                            color: '#374151',
                            maxHeight: '120px',
                            overflowY: 'auto'
                          }}>
                            {dayData.meals.map((meal, index) => {
                              const mealType = meal.meal_type || 'meal';
                              const mealName = meal.name || 'Unknown Meal';
                              return (
                                <div key={meal.id || index} style={{ marginBottom: '6px' }}>
                                  <span style={{ fontWeight: '600', color: '#059669' }}>
                                    {mealType.charAt(0).toUpperCase() + mealType.slice(1)}:
                                  </span>{' '}
                                  {mealName} ({meal.calories || 0} kcal)
                                </div>
                              );
                            })}
                          </div>
                        </div>
                        {/* Meal Tags */}
                        <div style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: '8px',
                        alignItems: 'center'
                      }}>
                        {dayData.meals.map((meal, index) => {
                          // Meal objects have properties: name, meal_type, calories, etc.
                          const mealType = meal.meal_type || 'meal';
                          const mealName = meal.name || 'Unknown Meal';

                          return (
                            <MealTag
                              key={meal.id || index}
                              meal={mealName}
                              mealType={mealType}
                            />
                          );
                        })}
                        </div>
                        </>
                    ) : (
                      /* Journal Tab Content */
                      <div>
                        {journalError && (
                        <div style={{
                            background: '#fef2f2',
                            border: '1px solid #fecaca',
                            color: '#dc2626',
                            padding: '8px 12px',
                            borderRadius: '8px',
                            fontSize: '13px',
                            marginBottom: '12px'
                          }}>
                            {journalError}
                        </div>
                        )}

                        {journalNote ? (
                        <div style={{
                            background: '#ffffff',
                            border: '1px solid #d1fae5',
                            color: '#374151',
                            padding: '16px',
                            borderRadius: '12px',
                            fontSize: '14px',
                            lineHeight: '1.6',
                            whiteSpace: 'pre-wrap',
                            marginBottom: '12px',
                            boxShadow: '0 1px 3px rgba(34, 197, 94, 0.08)'
                          }}>
                            {journalNote}
                        </div>
                        ) : (
                        <div style={{
                            background: '#f9fafb',
                            border: '2px dashed #bbf7d0',
                            borderRadius: '12px',
                            padding: '24px',
                            textAlign: 'center',
                          color: '#6b7280',
                            fontSize: '14px',
                            marginBottom: '12px'
                          }}>
                            <FileText width={24} height={24} style={{ marginBottom: '8px', opacity: 0.5 }} />
                            <div>No journal entry for this day</div>
                        </div>
                        )}

                        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                          <button
                            onClick={handleJournalEdit}
                            disabled={journalLoading}
                            style={{
                              padding: '8px 16px',
                              background: '#3b82f6',
                              border: 'none',
                              borderRadius: '8px',
                              fontSize: '13px',
                              fontWeight: '500',
                              color: '#ffffff',
                              cursor: journalLoading ? 'not-allowed' : 'pointer',
                              opacity: journalLoading ? 0.5 : 1,
                              transition: 'all 0.2s',
                        display: 'flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                          >
                            <Edit3 width={12} height={12} />
                            {journalNote ? 'Edit' : 'Add'} Journal Entry
                          </button>
                          {journalNote && (
                            <button
                              onClick={handleJournalDelete}
                              disabled={journalLoading}
                            style={{
                                padding: '8px 16px',
                                background: '#ef4444',
                                border: 'none',
                                borderRadius: '8px',
                                fontSize: '13px',
                              fontWeight: '500',
                                color: '#ffffff',
                                cursor: journalLoading ? 'not-allowed' : 'pointer',
                                opacity: journalLoading ? 0.5 : 1,
                                transition: 'all 0.2s',
                              display: 'flex',
                              alignItems: 'center',
                                gap: '4px'
                              }}
                            >
                              <Trash2 width={12} height={12} />
                              Delete
                            </button>
                          )}
                    </div>
                      </div>
                    )}
                  </motion.div>
                </>
              ) : hasNoteOnly ? (
                /* STATE 2: Note Card Display - Show saved note with edit/delete */
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h3 style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#111827',
                    marginBottom: '16px'
                  }}>
                    {isEditing ? 'Edit Note' : 'Your Note'}
                  </h3>
                  {isEditing ? (
                    /* Edit Mode - Show textarea */
                    <textarea
                      value={editedNote}
                      onChange={(e) => setEditedNote(e.target.value)}
                      placeholder="Write a note about your day..."
                      style={{
                        width: '100%',
                        minHeight: '200px',
                        padding: '16px',
                        fontSize: '15px',
                        lineHeight: '1.6',
                        color: '#374151',
                        background: '#ffffff',
                        border: '2px solid #e5e7eb',
                        borderRadius: '12px',
                        resize: 'vertical',
                        fontFamily: 'inherit',
                        outline: 'none',
                        transition: 'border-color 0.2s'
                      }}
                      onFocus={(e) => {
                        e.currentTarget.style.borderColor = '#f59e0b';
                      }}
                      onBlur={(e) => {
                        e.currentTarget.style.borderColor = '#e5e7eb';
                      }}
                      autoFocus
                    />
                  ) : (
                    /* Display Mode - Show note card */
                    <div style={{
                      background: 'linear-gradient(135deg, #fef3c7 0%, #fef9e7 100%)',
                      borderLeft: '4px solid #f59e0b',
                      color: '#92400e',
                      padding: '16px',
                      borderRadius: '12px',
                      marginBottom: '16px'
                    }}>
                      <p style={{
                        margin: 0,
                        fontSize: '15px',
                        lineHeight: '1.6',
                        whiteSpace: 'pre-wrap'
                      }}>
                        {dayData.note}
                      </p>
                    </div>
                  )}
                </motion.div>
              ) : (
                /* STATE 3: Input State - New day entry */
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: '12px'
                  }}>
                    <FileText width={18} height={18} color="#d97706" />
                    <h3 style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#6b7280',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                      margin: 0
                    }}>
                      Add a Note
                    </h3>
                  </div>
                  <textarea
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    placeholder="Write a note about your day... (e.g., energy levels, meal ideas, goals)"
                    style={{
                      width: '100%',
                      minHeight: '200px',
                      padding: '16px',
                      fontSize: '15px',
                      lineHeight: '1.6',
                      color: '#374151',
                      background: '#ffffff',
                      border: '2px solid #e5e7eb',
                      borderRadius: '12px',
                      resize: 'vertical',
                      fontFamily: 'inherit',
                      outline: 'none',
                      transition: 'border-color 0.2s'
                    }}
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#f59e0b';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                    }}
                  />
                </motion.div>
              )}
            </div>

            {/* Footer - Action Buttons */}
            <div style={{
              padding: '20px 24px',
              borderTop: '1px solid #e5e7eb',
              background: '#ffffff',
              display: 'flex',
              gap: '12px',
              justifyContent: 'flex-end'
            }}>
              {hasMealLog ? (
                /* Meal Log Buttons */
                <button
                  onClick={onClose}
                  style={{
                    padding: '12px 24px',
                    background: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '10px',
                    fontSize: '15px',
                    fontWeight: '600',
                    color: '#6b7280',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#f3f4f6';
                    e.currentTarget.style.borderColor = '#d1d5db';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#ffffff';
                    e.currentTarget.style.borderColor = '#e5e7eb';
                  }}
                >
                  Close
                </button>
              ) : hasNoteOnly ? (
                /* Note Card Buttons - Changes based on edit mode */
                isEditing ? (
                  /* Edit Mode Buttons (Cancel, Save) */
                  <>
                    <button
                      onClick={handleCancelEdit}
                      style={{
                        padding: '12px 24px',
                        background: '#ffffff',
                        border: '1px solid #e5e7eb',
                        borderRadius: '10px',
                        fontSize: '15px',
                        fontWeight: '600',
                        color: '#6b7280',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#f3f4f6';
                        e.currentTarget.style.borderColor = '#d1d5db';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#ffffff';
                        e.currentTarget.style.borderColor = '#e5e7eb';
                      }}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveEdit}
                      disabled={!editedNote.trim()}
                      style={{
                        padding: '12px 24px',
                        background: editedNote.trim()
                          ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                          : '#e5e7eb',
                        border: 'none',
                        borderRadius: '10px',
                        fontSize: '15px',
                        fontWeight: '600',
                        color: editedNote.trim() ? '#ffffff' : '#9ca3af',
                        cursor: editedNote.trim() ? 'pointer' : 'not-allowed',
                        transition: 'all 0.2s',
                        boxShadow: editedNote.trim()
                          ? '0 4px 6px -1px rgba(245, 158, 11, 0.3)'
                          : 'none'
                      }}
                      onMouseEnter={(e) => {
                        if (editedNote.trim()) {
                          e.currentTarget.style.transform = 'translateY(-2px)';
                          e.currentTarget.style.boxShadow = '0 6px 8px -1px rgba(245, 158, 11, 0.4)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (editedNote.trim()) {
                          e.currentTarget.style.transform = 'translateY(0)';
                          e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(245, 158, 11, 0.3)';
                        }
                      }}
                    >
                      Save Changes
                    </button>
                  </>
                ) : (
                  /* Display Mode Buttons (Close, Edit, Delete) */
                  <>
                    <button
                      onClick={onClose}
                      style={{
                        padding: '12px 24px',
                        background: '#ffffff',
                        border: '1px solid #e5e7eb',
                        borderRadius: '10px',
                        fontSize: '15px',
                        fontWeight: '600',
                        color: '#6b7280',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#f3f4f6';
                        e.currentTarget.style.borderColor = '#d1d5db';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#ffffff';
                        e.currentTarget.style.borderColor = '#e5e7eb';
                      }}
                    >
                      Close
                    </button>
                    <button
                      onClick={handleEditClick}
                      style={{
                        padding: '12px 24px',
                        background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                        border: 'none',
                        borderRadius: '10px',
                        fontSize: '15px',
                        fontWeight: '600',
                        color: '#ffffff',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.3)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = '0 6px 8px -1px rgba(59, 130, 246, 0.4)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(59, 130, 246, 0.3)';
                      }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        if (onDelete) {
                          onDelete(selectedDate);
                          onClose();
                        }
                      }}
                      style={{
                        padding: '12px 24px',
                        background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                        border: 'none',
                        borderRadius: '10px',
                        fontSize: '15px',
                        fontWeight: '600',
                        color: '#ffffff',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        boxShadow: '0 4px 6px -1px rgba(239, 68, 68, 0.3)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = '0 6px 8px -1px rgba(239, 68, 68, 0.4)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(239, 68, 68, 0.3)';
                      }}
                    >
                      Delete
                    </button>
                  </>
                )
              ) : (
                /* New Entry Input Buttons */
                <>
                  <button
                    onClick={onClose}
                    style={{
                      padding: '12px 24px',
                      background: '#ffffff',
                      border: '1px solid #e5e7eb',
                      borderRadius: '10px',
                      fontSize: '15px',
                      fontWeight: '600',
                      color: '#6b7280',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = '#f3f4f6';
                      e.currentTarget.style.borderColor = '#d1d5db';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = '#ffffff';
                      e.currentTarget.style.borderColor = '#e5e7eb';
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSaveNote}
                    disabled={!note.trim()}
                    style={{
                      padding: '12px 24px',
                      background: note.trim()
                        ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                        : '#e5e7eb',
                      border: 'none',
                      borderRadius: '10px',
                      fontSize: '15px',
                      fontWeight: '600',
                      color: note.trim() ? '#ffffff' : '#9ca3af',
                      cursor: note.trim() ? 'pointer' : 'not-allowed',
                      transition: 'all 0.2s',
                      boxShadow: note.trim()
                        ? '0 4px 6px -1px rgba(245, 158, 11, 0.3)'
                        : 'none'
                    }}
                    onMouseEnter={(e) => {
                      if (note.trim()) {
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = '0 6px 8px -1px rgba(245, 158, 11, 0.4)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (note.trim()) {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(245, 158, 11, 0.3)';
                      }
                    }}
                  >
                    Save Note
                  </button>
                </>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Journal Writing Window Modal */}
      <AnimatePresence>
        {showJournalWindow && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1300,
              zIndex: 1301,
              padding: '20px'
            }}
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                handleJournalCancel();
              }
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              style={{
                background: '#ffffff',
                borderRadius: '16px',
                padding: '24px',
                width: '100%',
                maxWidth: '600px',
                maxHeight: '80vh',
                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              {/* Header */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '20px',
                paddingBottom: '16px',
                borderBottom: '1px solid #e5e7eb'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <FileText width={20} height={20} style={{ color: '#3b82f6' }} />
                  <h2 style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: '#111827',
                    margin: 0
                  }}>
                    Journal Entry
                  </h2>
                </div>
                <button
                  onClick={handleJournalCancel}
                  style={{
                    background: 'none',
                    border: 'none',
                    fontSize: '20px',
                    color: '#6b7280',
                    cursor: 'pointer',
                    padding: '4px',
                    borderRadius: '4px',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#f3f4f6';
                    e.currentTarget.style.color = '#374151';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'none';
                    e.currentTarget.style.color = '#6b7280';
                  }}
                >
                  ×
                </button>
              </div>

              {/* Date Display */}
              <div style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '12px',
                marginBottom: '20px',
                fontSize: '14px',
                color: '#475569',
                fontWeight: '500'
              }}>
                📅 {formattedDate}
              </div>

              {/* Error Display */}
              {journalError && (
                <div style={{
                  background: '#fef2f2',
                  border: '1px solid #fecaca',
                  color: '#dc2626',
                  padding: '12px',
                  borderRadius: '8px',
                  fontSize: '14px',
                  marginBottom: '16px'
                }}>
                  {journalError}
                </div>
              )}

              {/* Textarea */}
              <textarea
                value={journalNote}
                onChange={(e) => setJournalNote(e.target.value)}
                placeholder="Write your thoughts about this day... What did you eat? How did you feel? Any insights or reflections?"
                style={{
                  width: '100%',
                  minHeight: '200px',
                  padding: '16px',
                  fontSize: '14px',
                  lineHeight: '1.6',
                  color: '#374151',
                  background: '#ffffff',
                  border: '2px solid #e5e7eb',
                  borderRadius: '12px',
                  resize: 'vertical',
                  fontFamily: 'inherit',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                  flex: 1
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#3b82f6';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#e5e7eb';
                }}
              />

              {/* Action Buttons */}
              <div style={{
                display: 'flex',
                justifyContent: 'flex-end',
                gap: '12px',
                marginTop: '20px',
                paddingTop: '16px',
                borderTop: '1px solid #e5e7eb'
              }}>
                <button
                  onClick={handleJournalCancel}
                  disabled={journalLoading}
                  style={{
                    padding: '10px 20px',
                    background: '#f3f4f6',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#6b7280',
                    cursor: journalLoading ? 'not-allowed' : 'pointer',
                    opacity: journalLoading ? 0.5 : 1,
                    transition: 'all 0.2s'
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleJournalSaveAndClose}
                  disabled={journalLoading || !journalNote.trim()}
                  style={{
                    padding: '10px 20px',
                    background: journalNote.trim() ? '#22c55e' : '#d1d5db',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: journalNote.trim() ? '#ffffff' : '#9ca3af',
                    cursor: (journalLoading || !journalNote.trim()) ? 'not-allowed' : 'pointer',
                    opacity: journalLoading ? 0.5 : 1,
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  <Save width={14} height={14} />
                  {journalLoading ? 'Saving...' : 'Save & Close'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </AnimatePresence>
  );
};

export default DayDetailModal;

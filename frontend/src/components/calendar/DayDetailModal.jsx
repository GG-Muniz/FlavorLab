import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Calendar as CalendarIcon, TrendingUp, FileText, Edit3, Save, Trash2 } from 'lucide-react';
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

  if (!selectedDate) return null;

  // Format the date nicely
  const formattedDate = moment(selectedDate).format('dddd, MMMM D, YYYY');
  const dateKey = moment(selectedDate).format('YYYY-MM-DD');

  // Determine which state to render based on data structure
  const hasMealLog = dayData && dayData.totals;
  const hasNoteOnly = dayData && dayData.note && !dayData.totals;

  // Load journal note when modal opens
  useEffect(() => {
    if (isOpen && selectedDate) {
      loadJournalNote();
    }
  }, [isOpen, selectedDate]);

  // Load journal note for the selected date
  const loadJournalNote = async () => {
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

  // Handle journal edit start
  const handleJournalEdit = () => {
    setIsJournalEditing(true);
  };

  // Handle journal edit cancel
  const handleJournalCancel = () => {
    setIsJournalEditing(false);
    setJournalError(null);
  };

  // NutritionTag component for displaying nutrition values as chips
  const NutritionTag = ({ label, value, unit, icon, color }) => (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      background: color || '#f3f4f6',
      color: '#374151',
      padding: '8px 12px',
      borderRadius: '20px',
      fontSize: '14px',
      fontWeight: '600',
      border: '1px solid #e5e7eb'
    }}>
      <span style={{ fontSize: '16px' }}>{icon}</span>
      <span>{label}: {value}{unit}</span>
    </div>
  );

  // MealTag component for displaying meals as chips
  const MealTag = ({ meal, mealType }) => (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      background: '#fef3c7',
      color: '#92400e',
      padding: '6px 12px',
      borderRadius: '16px',
      fontSize: '13px',
      fontWeight: '500',
      border: '1px solid #fbbf24'
    }}>
      <span style={{ fontSize: '12px', textTransform: 'capitalize' }}>{mealType}:</span>
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
        <>
          {/* Backdrop */}
          <motion.div
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
              background: 'rgba(102, 126, 234, 0.3)',
              backdropFilter: 'blur(8px)',
              zIndex: 1000,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px'
            }}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            style={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '90%',
              maxWidth: '600px',
              maxHeight: '80vh',
              background: '#ffffff',
              borderRadius: '24px',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              zIndex: 1001,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div style={{
              padding: '24px',
              borderBottom: '1px solid #f3f4f6',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              background: hasMealLog
                ? 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)'
                : hasNoteOnly
                ? 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
                : 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
            }}>
              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '8px'
                }}>
                  <CalendarIcon
                    width={20}
                    height={20}
                    color={hasMealLog ? '#16a34a' : '#d97706'}
                  />
                  <h2 style={{
                    fontSize: '24px',
                    fontWeight: '700',
                    color: '#111827',
                    margin: 0
                  }}>
                    {hasMealLog ? 'Health Journal' : hasNoteOnly ? 'Your Note' : 'New Entry'}
                  </h2>
                </div>
                <p style={{
                  fontSize: '14px',
                  color: '#6b7280',
                  margin: 0,
                  fontWeight: '500'
                }}>
                  {formattedDate}
                </p>
              </div>
              <button
                onClick={onClose}
                style={{
                  padding: '8px',
                  background: 'rgba(255, 255, 255, 0.8)',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#ffffff';
                  e.currentTarget.style.transform = 'scale(1.05)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.8)';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <X width={20} height={20} color="#6b7280" />
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
                      padding: '20px',
                      background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
                      borderRadius: '16px',
                      border: '1px solid #bae6fd',
                      marginBottom: '24px'
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      marginBottom: '16px'
                    }}>
                      <TrendingUp width={18} height={18} color="#0369a1" />
                      <h3 style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#0369a1',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        margin: 0
                      }}>
                        Daily Totals
                      </h3>
                    </div>
                    <div style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '8px',
                      alignItems: 'center'
                    }}>
                      <NutritionTag
                        label="Calories"
                        value={dayData.totals.calories}
                        unit=" kcal"
                        icon="🔥"
                        color="#fef2f2"
                      />
                      <NutritionTag
                        label="Protein"
                        value={dayData.totals.protein}
                        unit="g"
                        icon="🥩"
                        color="#f0fdf4"
                      />
                      <NutritionTag
                        label="Carbs"
                        value={dayData.totals.carbs}
                        unit="g"
                        icon="🌾"
                        color="#fffbeb"
                      />
                      <NutritionTag
                        label="Fat"
                        value={dayData.totals.fat}
                        unit="g"
                        icon="🥑"
                        color="#f0f9ff"
                      />
                      <NutritionTag
                        label="Fiber"
                        value={dayData.totals.fiber}
                        unit="g"
                        icon="🌿"
                        color="#f0fdf4"
                      />
                    </div>
                  </motion.div>

                  {/* Logged Meals List */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    <h3 style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#6b7280',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                      marginBottom: '12px'
                    }}>
                      Meals
                    </h3>
                    <div style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '8px',
                      alignItems: 'center'
                    }}>
                      {dayData.meals.map((meal, index) => {
                        // Extract meal type from meal string (e.g., "breakfast: Oatmeal" -> "breakfast")
                        const mealType = meal.split(':')[0]?.trim() || 'meal';
                        const mealName = meal.split(':').slice(1).join(':').trim() || meal;

                        return (
                          <MealTag
                            key={index}
                            meal={mealName}
                            mealType={mealType}
                          />
                        );
                      })}
                    </div>
                  </motion.div>

                  {/* Journal Section */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '12px'
                    }}>
                      <h3 style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#6b7280',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                        margin: 0
                      }}>
                        Journal
                      </h3>
                      {!isJournalEditing && journalNote && (
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button
                            onClick={handleJournalEdit}
                            disabled={journalLoading}
                            style={{
                              padding: '6px 12px',
                              background: '#f3f4f6',
                              border: '1px solid #d1d5db',
                              borderRadius: '8px',
                              fontSize: '12px',
                              fontWeight: '500',
                              color: '#6b7280',
                              cursor: journalLoading ? 'not-allowed' : 'pointer',
                              opacity: journalLoading ? 0.5 : 1,
                              transition: 'all 0.2s',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                            onMouseEnter={(e) => {
                              if (!journalLoading) {
                                e.currentTarget.style.background = '#e5e7eb';
                                e.currentTarget.style.borderColor = '#9ca3af';
                              }
                            }}
                            onMouseLeave={(e) => {
                              if (!journalLoading) {
                                e.currentTarget.style.background = '#f3f4f6';
                                e.currentTarget.style.borderColor = '#d1d5db';
                              }
                            }}
                          >
                            <Edit3 width={12} height={12} />
                            Edit
                          </button>
                          <button
                            onClick={handleJournalDelete}
                            disabled={journalLoading}
                            style={{
                              padding: '6px 12px',
                              background: '#fef2f2',
                              border: '1px solid #fecaca',
                              borderRadius: '8px',
                              fontSize: '12px',
                              fontWeight: '500',
                              color: '#dc2626',
                              cursor: journalLoading ? 'not-allowed' : 'pointer',
                              opacity: journalLoading ? 0.5 : 1,
                              transition: 'all 0.2s',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                            onMouseEnter={(e) => {
                              if (!journalLoading) {
                                e.currentTarget.style.background = '#fee2e2';
                                e.currentTarget.style.borderColor = '#fca5a5';
                              }
                            }}
                            onMouseLeave={(e) => {
                              if (!journalLoading) {
                                e.currentTarget.style.background = '#fef2f2';
                                e.currentTarget.style.borderColor = '#fecaca';
                              }
                            }}
                          >
                            <Trash2 width={12} height={12} />
                            Delete
                          </button>
                        </div>
                      )}
                    </div>

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

                    {isJournalEditing ? (
                      <div style={{
                        background: '#ffffff',
                        border: '2px solid #e5e7eb',
                        borderRadius: '12px',
                        padding: '16px'
                      }}>
                        <textarea
                          value={journalNote}
                          onChange={(e) => setJournalNote(e.target.value)}
                          placeholder="Write your thoughts about this day..."
                          style={{
                            width: '100%',
                            minHeight: '120px',
                            padding: '12px',
                            fontSize: '14px',
                            lineHeight: '1.5',
                            color: '#374151',
                            background: 'transparent',
                            border: 'none',
                            borderRadius: '8px',
                            resize: 'vertical',
                            fontFamily: 'inherit',
                            outline: 'none'
                          }}
                        />
                        <div style={{
                          display: 'flex',
                          justifyContent: 'flex-end',
                          gap: '8px',
                          marginTop: '12px'
                        }}>
                          <button
                            onClick={handleJournalCancel}
                            disabled={journalLoading}
                            style={{
                              padding: '8px 16px',
                              background: '#f3f4f6',
                              border: '1px solid #d1d5db',
                              borderRadius: '8px',
                              fontSize: '13px',
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
                            onClick={handleJournalSave}
                            disabled={journalLoading || !journalNote.trim()}
                            style={{
                              padding: '8px 16px',
                              background: journalNote.trim() ? '#22c55e' : '#d1d5db',
                              border: 'none',
                              borderRadius: '8px',
                              fontSize: '13px',
                              fontWeight: '500',
                              color: journalNote.trim() ? '#ffffff' : '#9ca3af',
                              cursor: (journalLoading || !journalNote.trim()) ? 'not-allowed' : 'pointer',
                              opacity: journalLoading ? 0.5 : 1,
                              transition: 'all 0.2s',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                          >
                            <Save width={12} height={12} />
                            {journalLoading ? 'Saving...' : 'Save'}
                          </button>
                        </div>
                      </div>
                    ) : journalNote ? (
                      <div style={{
                        background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
                        borderLeft: '4px solid #0ea5e9',
                        color: '#0c4a6e',
                        padding: '16px',
                        borderRadius: '12px',
                        fontSize: '14px',
                        lineHeight: '1.6',
                        whiteSpace: 'pre-wrap'
                      }}>
                        {journalNote}
                      </div>
                    ) : (
                      <div style={{
                        background: '#f9fafb',
                        border: '2px dashed #d1d5db',
                        borderRadius: '12px',
                        padding: '24px',
                        textAlign: 'center',
                        color: '#6b7280',
                        fontSize: '14px'
                      }}>
                        <FileText width={24} height={24} style={{ marginBottom: '8px', opacity: 0.5 }} />
                        <div>No journal entry for this day</div>
                        <button
                          onClick={handleJournalEdit}
                          disabled={journalLoading}
                          style={{
                            marginTop: '12px',
                            padding: '8px 16px',
                            background: '#3b82f6',
                            border: 'none',
                            borderRadius: '8px',
                            fontSize: '13px',
                            fontWeight: '500',
                            color: '#ffffff',
                            cursor: journalLoading ? 'not-allowed' : 'pointer',
                            opacity: journalLoading ? 0.5 : 1,
                            transition: 'all 0.2s'
                          }}
                        >
                          Add Journal Entry
                        </button>
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
              borderTop: '1px solid #f3f4f6',
              background: '#f9fafb',
              display: 'flex',
              gap: '12px',
              justifyContent: 'flex-end'
            }}>
              {hasMealLog ? (
                /* Meal Log Buttons */
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
                    onClick={handleViewFullLog}
                    style={{
                      padding: '12px 24px',
                      background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                      border: 'none',
                      borderRadius: '10px',
                      fontSize: '15px',
                      fontWeight: '600',
                      color: '#ffffff',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      boxShadow: '0 4px 6px -1px rgba(34, 197, 94, 0.3)'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = '0 6px 8px -1px rgba(34, 197, 94, 0.4)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(34, 197, 94, 0.3)';
                    }}
                  >
                    View Full Log
                  </button>
                </>
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
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default DayDetailModal;

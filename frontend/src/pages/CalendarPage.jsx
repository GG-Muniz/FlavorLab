import { useState, useMemo, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import moment from 'moment';
import DayDetailModal from '../components/calendar/DayDetailModal';

// Default mock data representing days with logged meals
const defaultMockLoggedDays = {
  '2025-10-05': {
    totals: { calories: 2200, protein: 150, carbs: 250, fat: 70 },
    meals: ['Breakfast', 'Lunch', 'Dinner'],
  },
  '2025-10-12': {
    totals: { calories: 1950, protein: 130, carbs: 200, fat: 65 },
    meals: ['Breakfast', 'Snack', 'Dinner'],
  },
  '2025-10-14': {
    totals: { calories: 2100, protein: 160, carbs: 220, fat: 75 },
    meals: ['Lunch', 'Post-Workout Shake', 'Dinner'],
  },
};

const CalendarPage = () => {
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedDayData, setSelectedDayData] = useState(null);
  const [isNew, setIsNew] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [loggedDays, setLoggedDays] = useState({});
  const [currentMonth, setCurrentMonth] = useState(moment());

  // Load data from localStorage on initial mount
  useEffect(() => {
    const storedData = localStorage.getItem('healthLabCalendarData');
    if (storedData) {
      try {
        const parsedData = JSON.parse(storedData);
        setLoggedDays(parsedData);
      } catch (error) {
        console.error('Error parsing localStorage data:', error);
        setLoggedDays(defaultMockLoggedDays);
      }
    } else {
      setLoggedDays(defaultMockLoggedDays);
    }
  }, []);

  // Handle saving day data (notes or meal data)
  const handleSaveDay = (date, newData) => {
    const dateKey = moment(date).format('YYYY-MM-DD');

    // Create a new copy of loggedDays
    const updatedLoggedDays = {
      ...loggedDays,
      [dateKey]: {
        ...loggedDays[dateKey],
        ...newData
      }
    };

    // Update state
    setLoggedDays(updatedLoggedDays);

    // Save to localStorage
    localStorage.setItem('healthLabCalendarData', JSON.stringify(updatedLoggedDays));
  };

  // Handle deleting day data
  const handleDeleteDay = (dateToDelete) => {
    const dateKey = moment(dateToDelete).format('YYYY-MM-DD');
    console.log(`ACTION: Deleting data for ${dateKey}`);

    // Create a new copy and delete the key
    const updatedDays = { ...loggedDays };
    delete updatedDays[dateKey];

    // Update state
    setLoggedDays(updatedDays);

    // Save to localStorage
    localStorage.setItem('healthLabCalendarData', JSON.stringify(updatedDays));
  };

  // Handle day selection
  const handleDayClick = (date) => {
    const dateKey = moment(date).format('YYYY-MM-DD');
    const dayData = loggedDays[dateKey];

    setSelectedDate(date.toDate());
    setSelectedDayData(dayData);
    setIsNew(!dayData);
    setShowModal(true);
  };

  // Handle modal close
  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedDate(null);
    setSelectedDayData(null);
  };

  // Navigate months
  const goToPreviousMonth = () => {
    setCurrentMonth(currentMonth.clone().subtract(1, 'month'));
  };

  const goToNextMonth = () => {
    setCurrentMonth(currentMonth.clone().add(1, 'month'));
  };

  // Generate calendar days
  const calendarDays = useMemo(() => {
    const startOfMonth = currentMonth.clone().startOf('month');
    const endOfMonth = currentMonth.clone().endOf('month');
    const startDate = startOfMonth.clone().startOf('week');
    const endDate = endOfMonth.clone().endOf('week');

    const days = [];
    const day = startDate.clone();

    while (day.isSameOrBefore(endDate, 'day')) {
      days.push(day.clone());
      day.add(1, 'day');
    }

    return days;
  }, [currentMonth]);

  // Get today's logged entries
  const todayEntries = useMemo(() => {
    const todayKey = moment().format('YYYY-MM-DD');
    const todayData = loggedDays[todayKey];

    if (!todayData) return [];

    const entries = [];
    if (todayData.meals) {
      entries.push({
        title: 'Meals Logged',
        time: `${todayData.meals.length} meals`,
        status: 'completed',
        color: '#4CAF50'
      });
    }
    if (todayData.note) {
      entries.push({
        title: 'Daily Note',
        time: 'Saved',
        status: 'completed',
        color: '#4CAF50'
      });
    }

    return entries;
  }, [loggedDays]);

  return (
    <div style={{
      minHeight: '100vh',
      background: '#F8F9FA',
      padding: '20px',
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'center',
      paddingTop: '40px'
    }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        style={{
          width: '100%',
          maxWidth: '900px',
          display: 'grid',
          gridTemplateColumns: '1fr 380px',
          gap: '20px',
          alignItems: 'start'
        }}
      >
        {/* Main Calendar Card - Soft Pastel Green */}
        <div style={{
          background: '#E6F4EA',
          borderRadius: '16px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04)',
          overflow: 'hidden'
        }}>
          {/* Header */}
          <div style={{
            padding: '24px 24px 16px 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid rgba(76, 175, 80, 0.15)'
          }}>
            <h2 style={{
              fontSize: '22px',
              fontWeight: '600',
              color: '#2C3E50',
              margin: 0,
              letterSpacing: '-0.5px'
            }}>
              {currentMonth.format('MMMM YYYY')}
            </h2>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={goToPreviousMonth}
                style={{
                  background: 'rgba(255, 255, 255, 0.7)',
                  border: 'none',
                  borderRadius: '10px',
                  width: '36px',
                  height: '36px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.95)';
                  e.currentTarget.style.transform = 'scale(1.05)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.7)';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <ChevronLeft size={20} color="#2C3E50" />
              </button>

              <button
                onClick={goToNextMonth}
                style={{
                  background: 'rgba(255, 255, 255, 0.7)',
                  border: 'none',
                  borderRadius: '10px',
                  width: '36px',
                  height: '36px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.95)';
                  e.currentTarget.style.transform = 'scale(1.05)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.7)';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <ChevronRight size={20} color="#2C3E50" />
              </button>
            </div>
          </div>

          {/* Calendar Grid */}
          <div style={{ padding: '20px 24px 24px 24px' }}>
            {/* Day headers */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(7, 1fr)',
              gap: '6px',
              marginBottom: '12px'
            }}>
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, index) => (
                <div
                  key={index}
                  style={{
                    fontSize: '12px',
                    fontWeight: '600',
                    color: '#5F6368',
                    textAlign: 'center',
                    padding: '8px 0',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar days */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(7, 1fr)',
              gap: '6px'
            }}>
              {calendarDays.map((day, index) => {
                const isToday = day.isSame(moment(), 'day');
                const isCurrentMonth = day.isSame(currentMonth, 'month');
                const dateKey = day.format('YYYY-MM-DD');
                const hasData = loggedDays[dateKey];

                return (
                  <motion.button
                    key={index}
                    onClick={() => handleDayClick(day)}
                    whileHover={{ scale: 1.08 }}
                    whileTap={{ scale: 0.95 }}
                    style={{
                      background: isToday
                        ? '#4CAF50'
                        : 'rgba(255, 255, 255, 0.5)',
                      border: isToday ? 'none' : hasData ? '2px solid #4CAF50' : 'none',
                      borderRadius: '12px',
                      aspectRatio: '1',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '15px',
                      fontWeight: isToday ? '600' : '500',
                      color: isToday
                        ? 'white'
                        : isCurrentMonth
                          ? '#2C3E50'
                          : '#9CA3AF',
                      cursor: 'pointer',
                      position: 'relative',
                      transition: 'all 0.2s'
                    }}
                  >
                    {day.format('D')}
                    {hasData && !isToday && (
                      <div style={{
                        position: 'absolute',
                        bottom: '6px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        width: '5px',
                        height: '5px',
                        borderRadius: '50%',
                        background: '#4CAF50'
                      }} />
                    )}
                  </motion.button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Sidebar - Today Section - Soft Pastel Yellow */}
        <div style={{
          background: '#FFF9E6',
          borderRadius: '16px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04)',
          padding: '24px',
          position: 'sticky',
          top: '40px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '20px'
          }}>
            <h3 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#2C3E50',
              margin: 0,
              letterSpacing: '-0.3px'
            }}>
              Today
            </h3>

            <motion.button
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                setSelectedDate(new Date());
                setSelectedDayData(loggedDays[moment().format('YYYY-MM-DD')]);
                setIsNew(!loggedDays[moment().format('YYYY-MM-DD')]);
                setShowModal(true);
              }}
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '20px',
                background: '#FF9966',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                boxShadow: '0 3px 10px rgba(255, 153, 102, 0.35)',
                transition: 'all 0.2s'
              }}
            >
              <Plus size={22} color="white" strokeWidth={2.5} />
            </motion.button>
          </div>

          <div style={{
            fontSize: '14px',
            color: '#5F6368',
            marginBottom: '20px',
            fontWeight: '500'
          }}>
            {moment().format('dddd, MMMM D')}
          </div>

          {/* Entries list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {todayEntries.length > 0 ? (
              todayEntries.map((entry, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '16px',
                    background: 'rgba(255, 255, 255, 0.7)',
                    borderRadius: '14px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    border: '1px solid rgba(76, 175, 80, 0.1)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.95)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.7)';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                  onClick={() => {
                    setSelectedDate(new Date());
                    setSelectedDayData(loggedDays[moment().format('YYYY-MM-DD')]);
                    setIsNew(false);
                    setShowModal(true);
                  }}
                >
                  <div style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    background: entry.color,
                    flexShrink: 0
                  }} />
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: '15px',
                      fontWeight: '600',
                      color: '#2C3E50',
                      marginBottom: '3px'
                    }}>
                      {entry.title}
                    </div>
                    <div style={{
                      fontSize: '13px',
                      color: '#5F6368',
                      fontWeight: '500'
                    }}>
                      {entry.time}
                    </div>
                  </div>
                  <div style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: '12px',
                    background: entry.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    <div style={{
                      width: '10px',
                      height: '6px',
                      borderLeft: '2.5px solid white',
                      borderBottom: '2.5px solid white',
                      transform: 'rotate(-45deg) translateY(-1px)',
                      marginLeft: '1px'
                    }} />
                  </div>
                </motion.div>
              ))
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '48px 20px',
                color: '#9CA3AF',
                fontSize: '14px'
              }}>
                <div style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '28px',
                  background: 'rgba(255, 255, 255, 0.7)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px'
                }}>
                  <Plus size={28} color="#C7C7CC" strokeWidth={2} />
                </div>
                <div style={{ fontWeight: '500' }}>No entries for today</div>
                <div style={{ fontSize: '12px', marginTop: '6px', color: '#B0B0B0' }}>
                  Click + to add one
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Modal */}
      <DayDetailModal
        isOpen={showModal}
        onClose={handleCloseModal}
        selectedDate={selectedDate}
        dayData={selectedDayData}
        isNew={isNew}
        onSave={handleSaveDay}
        onDelete={handleDeleteDay}
      />
    </div>
  );
};

export default CalendarPage;

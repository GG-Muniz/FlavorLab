import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import DayDetailModal from './DayDetailModal';
import { useData } from '../../context/DataContext';

const Calendar = () => {
  const { getMealsForDate, getNutritionSummaryForDate } = useData();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);
  const [showDayDetail, setShowDayDetail] = useState(false);
  const [monthData, setMonthData] = useState({});
  const [selectedDayData, setSelectedDayData] = useState(null);
  const [isLoadingDayData, setIsLoadingDayData] = useState(false);

  // Get the first day of the month
  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  };

  // Get the last day of the month
  const getLastDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0);
  };

  // Get the day of week (0 = Sunday, 6 = Saturday)
  const getDayOfWeek = (date) => {
    return date.getDay();
  };

  // Get number of days in month
  const getDaysInMonth = (date) => {
    return getLastDayOfMonth(date).getDate();
  };

  // Navigate to previous month
  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  // Navigate to next month
  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  // Go to today
  const goToToday = () => {
    const today = new Date();
    setCurrentDate(today);
    setSelectedDate(today);
  };

  // Check if two dates are the same day
  const isSameDay = (date1, date2) => {
    return date1.getDate() === date2.getDate() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getFullYear() === date2.getFullYear();
  };

  // Check if date is today
  const isToday = (date) => {
    return isSameDay(date, new Date());
  };

  // Fetch month data - load all logged meals to determine which days have data
  useEffect(() => {
    const fetchMonthData = async () => {
      try {
        // For now, we'll fetch data on-demand when a day is clicked
        // This prevents loading too much data upfront
        // We could optimize later by caching the current month's meals
        setMonthData({});
      } catch (error) {
        console.error("Error fetching month data:", error);
      }
    };

    fetchMonthData();
  }, [currentDate]);

  // Handle day click - fetch real data from backend
  const handleDayClick = async (day) => {
    setSelectedDate(day);
    setIsLoadingDayData(true);

    const dateKey = `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}`;

    try {
      // Fetch both meals and nutrition summary for the selected date
      const [meals, nutritionSummary] = await Promise.all([
        getMealsForDate(dateKey),
        getNutritionSummaryForDate(dateKey)
      ]);

      if (meals.length > 0) {
        // Format data to match DayDetailModal expectations
        setSelectedDayData({
          date: dateKey,
          meals: meals.map(meal => `${meal.meal_type}: ${meal.name} (${meal.calories} cal)`),
          totals: {
            calories: Math.round(nutritionSummary.total_calories || 0),
            protein: Math.round(nutritionSummary.total_protein_g || 0),
            carbs: Math.round(nutritionSummary.total_carbs_g || 0),
            fat: Math.round(nutritionSummary.total_fat_g || 0),
            fiber: Math.round(nutritionSummary.total_fiber_g || 0)
          }
        });

        // Update monthData to show this day has a log
        setMonthData(prev => ({
          ...prev,
          [dateKey]: { hasLog: true }
        }));
      } else {
        setSelectedDayData(null);
      }
    } catch (error) {
      console.error("Error fetching day data:", error);
      setSelectedDayData(null);
    } finally {
      setIsLoadingDayData(false);
    }

    setShowDayDetail(true);
  };

  // Check if day has logged meals
  const dayHasLog = (day) => {
    if (!day) return false;
    const dateKey = `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}`;
    return monthData[dateKey]?.hasLog || false;
  };

  // Generate calendar days
  const generateCalendarDays = () => {
    const firstDay = getFirstDayOfMonth(currentDate);
    const daysInMonth = getDaysInMonth(currentDate);
    const startingDayOfWeek = getDayOfWeek(firstDay);

    const days = [];

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }

    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(currentDate.getFullYear(), currentDate.getMonth(), day));
    }

    return days;
  };

  const calendarDays = generateCalendarDays();
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: '16px',
      padding: '20px',
      boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
      border: '1px solid #f3f4f6'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <h2 style={{
          fontSize: '18px',
          fontWeight: '700',
          color: '#111827',
          margin: 0
        }}>
          {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
        </h2>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={goToToday}
            style={{
              padding: '8px 16px',
              background: '#f0fdf4',
              border: '1px solid #bbf7d0',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              color: '#16a34a',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#dcfce7';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#f0fdf4';
            }}
          >
            Today
          </button>

          <button
            onClick={goToPreviousMonth}
            style={{
              padding: '8px',
              background: 'transparent',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#f3f4f6';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
            }}
          >
            <ChevronLeft width={20} height={20} color="#6b7280" />
          </button>

          <button
            onClick={goToNextMonth}
            style={{
              padding: '8px',
              background: 'transparent',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#f3f4f6';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
            }}
          >
            <ChevronRight width={20} height={20} color="#6b7280" />
          </button>
        </div>
      </div>

      {/* Day names header */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(7, 1fr)',
        gap: '8px',
        marginBottom: '8px'
      }}>
        {dayNames.map((day) => (
          <div
            key={day}
            style={{
              textAlign: 'center',
              fontSize: '12px',
              fontWeight: '600',
              color: '#6b7280',
              padding: '8px 0',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(7, 1fr)',
        gap: '8px'
      }}>
        {calendarDays.map((day, index) => {
          if (!day) {
            return <div key={`empty-${index}`} />;
          }

          const isSelected = selectedDate && isSameDay(day, selectedDate);
          const isTodayDate = isToday(day);
          const hasLog = dayHasLog(day);

          return (
            <button
              key={index}
              onClick={() => handleDayClick(day)}
              style={{
                aspectRatio: '1',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
                fontSize: '14px',
                fontWeight: '600',
                border: hasLog 
                  ? '2px solid #22c55e' 
                  : isTodayDate 
                    ? '2px solid #22c55e' 
                    : '1px solid #e5e7eb',
                borderRadius: '10px',
                background: isSelected
                  ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
                  : isTodayDate 
                    ? '#f0fdf4' 
                    : '#ffffff',
                color: isSelected ? '#ffffff' : isTodayDate ? '#22c55e' : '#374151',
                cursor: 'pointer',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                position: 'relative',
                padding: '8px',
                minHeight: '60px'
              }}
              onMouseEnter={(e) => {
                if (!isSelected) {
                  e.currentTarget.style.transform = 'scale(1.05) translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(34, 197, 94, 0.15)';
                  e.currentTarget.style.background = '#f0fdf4';
                }
              }}
              onMouseLeave={(e) => {
                if (!isSelected) {
                  e.currentTarget.style.transform = 'scale(1) translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                  e.currentTarget.style.background = isTodayDate ? '#f0fdf4' : '#ffffff';
                }
              }}
            >
              <span>{day.getDate()}</span>
              {hasLog && (
                <div style={{
                  position: 'absolute',
                  bottom: '6px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: '4px',
                  height: '4px',
                  borderRadius: '50%',
                  background: isSelected ? '#ffffff' : '#22c55e'
                }} />
              )}
            </button>
          );
        })}
      </div>

      {/* Day Detail Modal */}
      <DayDetailModal
        isOpen={showDayDetail}
        onClose={() => setShowDayDetail(false)}
        selectedDate={selectedDate}
        dayData={selectedDayData}
        isLoading={isLoadingDayData}
      />
    </div>
  );
};

export default Calendar;

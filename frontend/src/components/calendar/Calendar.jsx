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

  // Fetch month data from API
  useEffect(() => {
    const fetchMonthData = async () => {
      const monthDataMap = {};
      const firstDay = getFirstDayOfMonth(currentDate);
      const lastDay = getLastDayOfMonth(currentDate);

      // Fetch data for each day in the current month
      for (let d = new Date(firstDay); d <= lastDay; d.setDate(d.getDate() + 1)) {
        const dateKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

        try {
          const meals = await getMealsForDate(dateKey);
          if (meals && meals.length > 0) {
            monthDataMap[dateKey] = { hasLog: true };
          }
        } catch (error) {
          console.error(`Error fetching data for ${dateKey}:`, error);
        }
      }

      setMonthData(monthDataMap);
    };

    fetchMonthData();
  }, [currentDate, getMealsForDate]);

  // Handle day click - open modal with day details
  const handleDayClick = async (day) => {
    setSelectedDate(day);
    setShowDayDetail(true);
    setIsLoadingDayData(true);

    const dateKey = `${day.getFullYear()}-${String(day.getMonth() + 1).padStart(2, '0')}-${String(day.getDate()).padStart(2, '0')}`;

    try {
      // Fetch real meals and nutrition summary from backend
      const [meals, nutritionSummary] = await Promise.all([
        getMealsForDate(dateKey),
        getNutritionSummaryForDate(dateKey)
      ]);

      if (meals && meals.length > 0) {
        // Transform API response to match DayDetailModal expected format
        setSelectedDayData({
          date: dateKey,
          meals: meals, // Array of meal objects with meal_type, name, calories, etc.
          totals: {
            calories: nutritionSummary.total_calories || 0,
            protein: nutritionSummary.total_protein_g || 0,
            carbs: nutritionSummary.total_carbs_g || 0,
            fat: nutritionSummary.total_fat_g || 0,
            fiber: nutritionSummary.total_fiber_g || 0
          }
        });
      } else {
        // No meals logged for this day
        setSelectedDayData(null);
      }
    } catch (error) {
      console.error('Error fetching day details:', error);
      setSelectedDayData(null);
    } finally {
      setIsLoadingDayData(false);
    }
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
      borderRadius: '20px',
      padding: '24px',
      boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
      border: '1px solid #f3f4f6'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <h2 style={{
          fontSize: '20px',
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
                border: isTodayDate ? '2px solid #22c55e' : '1px solid transparent',
                borderRadius: '12px',
                background: isSelected
                  ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
                  : 'transparent',
                color: isSelected ? '#ffffff' : isTodayDate ? '#22c55e' : '#374151',
                cursor: 'pointer',
                transition: 'all 0.2s',
                position: 'relative',
                padding: '8px'
              }}
              onMouseEnter={(e) => {
                if (!isSelected) {
                  e.currentTarget.style.background = '#f3f4f6';
                }
              }}
              onMouseLeave={(e) => {
                if (!isSelected) {
                  e.currentTarget.style.background = 'transparent';
                }
              }}
            >
              <span>{day.getDate()}</span>
              {hasLog && (
                <div style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: isSelected ? '#ffffff' : '#22c55e',
                  marginTop: '2px'
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

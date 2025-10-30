import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import flavorLabIcon from '../assets/healthlab-icon.png';

export default function LandingPage() {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    // Navbar scroll effect
    const handleScroll = () => {
      setScrolled(window.scrollY > 100);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    // Reveal animation on scroll
    const reveal = () => {
      const reveals = document.querySelectorAll('.reveal');

      for (let i = 0; i < reveals.length; i++) {
        const windowHeight = window.innerHeight;
        const elementTop = reveals[i].getBoundingClientRect().top;
        const elementVisible = 100;

        if (elementTop < windowHeight - elementVisible) {
          reveals[i].classList.add('active');
        }
      }
    };

    window.addEventListener('scroll', reveal);
    setTimeout(reveal, 100);

    return () => window.removeEventListener('scroll', reveal);
  }, []);

  const handleFormSubmit = (e) => {
    e.preventDefault();
    // Navigate to signup instead of showing alert
    navigate('/signup');
  };

  return (
    <div className="landing-page">
      <style>{`
        .landing-page * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        .landing-page {
            --primary: #3E9B5F;
            --primary-dark: #2d7a47;
            --primary-light: #5fb67d;
            --primary-lighter: #9FD356;
            --secondary: #3B82F6;
            --background: #FFFFFF;
            --surface: #F9FAFB;
            --surface-light: #F3F4F6;
            --text-primary: #111827;
            --text-secondary: #4B5563;
            --text-muted: #9CA3AF;
            --border: #E5E7EB;
            --border-light: #F3F4F6;
            --accent-yellow: #FEF3C7;
            --accent-blue: #DBEAFE;
            --accent-purple: #EDE9FE;
            --accent-pink: #FCE7F3;
            --gradient-primary: linear-gradient(135deg, #9FD356 0%, #3E9B5F 100%);
            --gradient-dark: linear-gradient(135deg, #1F2937 0%, #111827 100%);
            --gradient-light: linear-gradient(180deg, #FFFFFF 0%, #F9FAFB 100%);
            --gradient-mesh: radial-gradient(at 40% 20%, hsla(152, 68%, 50%, 0.15) 0px, transparent 50%),
                            radial-gradient(at 80% 0%, hsla(189, 100%, 56%, 0.1) 0px, transparent 50%),
                            radial-gradient(at 0% 50%, hsla(355, 100%, 93%, 0.1) 0px, transparent 50%);
        }

        .landing-page {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--text-primary);
            line-height: 1.6;
            background: var(--background);
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        html {
            scroll-behavior: smooth;
        }

        .landing-page ::selection {
            background: var(--primary-light);
            color: white;
        }

        .navbar {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border-bottom: 1px solid rgba(229, 231, 235, 0.6);
            z-index: 1000;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .navbar.scrolled {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
            background: rgba(255, 255, 255, 0.98);
        }

        .nav-container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 1.25rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .nav-logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            text-decoration: none;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            transition: transform 0.2s ease;
        }

        .nav-logo:hover {
            transform: scale(1.02);
        }

        .logo-mark {
            width: 42px;
            height: 42px;
            background: var(--gradient-primary);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2);
            transition: all 0.3s ease;
        }

        .nav-logo:hover .logo-mark {
            transform: rotate(-5deg);
            box-shadow: 0 6px 12px -1px rgba(16, 185, 129, 0.3);
        }

        .nav-menu {
            display: flex;
            gap: 2.5rem;
            align-items: center;
            list-style: none;
        }

        .nav-link {
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            position: relative;
            transition: color 0.2s ease;
            padding: 0.5rem 0;
        }

        .nav-link:hover {
            color: var(--text-primary);
        }

        .nav-link::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 0;
            height: 2px;
            background: var(--gradient-primary);
            transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .nav-link:hover::after {
            width: 100%;
        }

        .nav-cta {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.95rem;
            text-decoration: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            cursor: pointer;
            border: none;
            position: relative;
            overflow: hidden;
            white-space: nowrap;
        }

        .btn-primary {
            background: var(--gradient-primary);
            color: white;
            box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
            position: relative;
        }

        .btn-primary::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        .btn-primary:hover::before {
            width: 300px;
            height: 300px;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.4);
        }

        .btn-secondary {
            background: var(--surface);
            color: var(--text-primary);
            border: 2px solid var(--border);
            font-weight: 600;
        }

        .btn-secondary:hover {
            background: var(--surface-light);
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.1);
        }

        .btn-large {
            padding: 1.125rem 2.25rem;
            font-size: 1.05rem;
        }

        .hero {
            padding-top: 120px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            background: var(--gradient-mesh), var(--gradient-light);
            position: relative;
            overflow: hidden;
        }

        .hero::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -25%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 60%);
            animation: float 25s ease-in-out infinite;
        }

        .hero::after {
            content: '';
            position: absolute;
            bottom: -50%;
            left: -25%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.05) 0%, transparent 60%);
            animation: float 30s ease-in-out infinite reverse;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(30px, -30px) rotate(120deg); }
            66% { transform: translate(-20px, 20px) rotate(240deg); }
        }

        .hero-container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
            z-index: 1;
        }

        .hero-content {
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.375rem 1rem;
            background: white;
            border: 1px solid var(--border);
            border-radius: 100px;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 2rem;
            animation: fadeInDown 0.8s ease;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }

        .badge-new {
            background: var(--gradient-primary);
            color: white;
            padding: 0.125rem 0.5rem;
            border-radius: 100px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .hero-title {
            font-size: 4.5rem;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -0.03em;
            color: var(--text-primary);
            margin-bottom: 1.75rem;
            animation: fadeInUp 0.8s ease 0.1s backwards;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .gradient-text {
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: inline-block;
        }

        .hero-description {
            font-size: 1.375rem;
            color: var(--text-secondary);
            margin-bottom: 2.5rem;
            line-height: 1.6;
            animation: fadeInUp 0.8s ease 0.2s backwards;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        }

        .hero-actions {
            display: flex;
            gap: 1.25rem;
            justify-content: center;
            margin-bottom: 4rem;
            animation: fadeInUp 0.8s ease 0.3s backwards;
        }

        .product-preview {
            margin-top: 2rem;
            animation: fadeInUp 1s ease 0.5s backwards;
        }

        .preview-container {
            max-width: 1000px;
            margin: 0 auto;
            position: relative;
        }

        .browser-mockup {
            background: white;
            border-radius: 16px;
            box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            border: 1px solid var(--border-light);
            transform: perspective(1500px) rotateX(5deg);
            transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .browser-mockup:hover {
            transform: perspective(1500px) rotateX(0deg) scale(1.02);
        }

        .browser-header {
            background: var(--surface);
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .browser-dots {
            display: flex;
            gap: 0.5rem;
        }

        .browser-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--border);
        }

        .browser-dot:nth-child(1) { background: #FF5F57; }
        .browser-dot:nth-child(2) { background: #FFBD2E; }
        .browser-dot:nth-child(3) { background: #28CA42; }

        .browser-url {
            flex: 1;
            background: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            color: var(--text-muted);
            border: 1px solid var(--border-light);
        }

        .dashboard-content {
            padding: 0;
            background: #f5f5f5;
        }

        .dashboard-nav {
            background: white;
            border-bottom: 1px solid var(--border);
            display: flex;
            gap: 0;
        }

        .dashboard-nav-item {
            padding: 1rem 1.5rem;
            color: var(--text-secondary);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            font-weight: 500;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }

        .dashboard-nav-item:first-child {
            background: #3E9B5F;
            color: white;
            border-bottom: 3px solid #2d7a47;
        }

        .dashboard-main {
            padding: 2rem;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1.5rem;
        }

        .calories-card {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .calories-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
        }

        .calories-icon {
            color: #3E9B5F;
            font-size: 1.25rem;
        }

        .calories-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .calories-progress {
            position: relative;
            width: 120px;
            height: 120px;
            margin: 1.5rem auto;
        }

        .progress-ring {
            transform: rotate(-90deg);
        }

        .progress-ring-bg {
            fill: none;
            stroke: #f0f0f0;
            stroke-width: 8;
        }

        .progress-ring-fill {
            fill: none;
            stroke: #3E9B5F;
            stroke-width: 8;
            stroke-linecap: round;
            stroke-dasharray: 283;
            stroke-dashoffset: 265;
            transition: stroke-dashoffset 0.5s ease;
        }

        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }

        .progress-percentage {
            font-size: 2rem;
            font-weight: 700;
            color: #3E9B5F;
            line-height: 1;
        }

        .calories-stats {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin-top: 1rem;
        }

        .calorie-stat {
            display: flex;
            justify-content: space-between;
            font-size: 0.875rem;
        }

        .stat-label {
            color: var(--text-secondary);
        }

        .stat-value {
            font-weight: 600;
            color: var(--text-primary);
        }

        .add-meal-btn {
            width: 100%;
            padding: 0.875rem;
            background: #3E9B5F;
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            margin-top: 1rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            transition: all 0.3s ease;
        }

        .add-meal-btn:hover {
            background: #2d7a47;
            transform: translateY(-1px);
        }

        .macros-card {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .macros-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
        }

        .macros-icon {
            color: #3E9B5F;
            font-size: 1.25rem;
        }

        .macros-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .macro-item {
            margin-bottom: 1.5rem;
        }

        .macro-item:last-child {
            margin-bottom: 0;
        }

        .macro-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }

        .macro-name {
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text-primary);
        }

        .macro-values {
            font-size: 0.875rem;
            color: var(--text-secondary);
        }

        .macro-progress-bar {
            width: 100%;
            height: 8px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
        }

        .macro-progress-fill {
            height: 100%;
            background: var(--gradient-primary);
            border-radius: 10px;
            transition: width 0.5s ease;
        }

        .macro-progress-fill.protein { background: #10B981; width: 20%; }
        .macro-progress-fill.carbs { background: #F59E0B; width: 70%; }
        .macro-progress-fill.fat { background: #EF4444; width: 65%; }
        .macro-progress-fill.fiber { background: #3B82F6; width: 28%; }

        .activity-card {
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .activity-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
        }

        .activity-icon {
            color: #3E9B5F;
            font-size: 1.25rem;
        }

        .activity-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .activity-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.25rem;
            background: #f9f9f9;
            border-radius: 12px;
            margin-bottom: 1rem;
        }

        .activity-item:last-child {
            margin-bottom: 0;
        }

        .activity-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .activity-item-icon {
            width: 42px;
            height: 42px;
            background: white;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }

        .activity-info {
            display: flex;
            flex-direction: column;
        }

        .activity-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.25rem;
        }

        .activity-value {
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-primary);
        }

        .activity-sub {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        .activity-count {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .streak-badge {
            background: #FEF3C7;
            color: #92400E;
            padding: 1.25rem;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .streak-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .streak-icon {
            width: 42px;
            height: 42px;
            background: white;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }

        .streak-info {
            display: flex;
            flex-direction: column;
        }

        .streak-title {
            font-weight: 600;
            margin-bottom: 0.125rem;
        }

        .streak-subtitle {
            font-size: 0.75rem;
            opacity: 0.8;
        }

        .streak-days {
            text-align: center;
        }

        .streak-count {
            font-size: 2rem;
            font-weight: 700;
            line-height: 1;
        }

        .streak-label {
            font-size: 0.75rem;
            opacity: 0.8;
        }

        .features {
            padding: 120px 0;
            background: white;
            position: relative;
        }

        .features::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--border), transparent);
        }

        .section-header {
            text-align: center;
            max-width: 800px;
            margin: 0 auto 5rem;
        }

        .section-badge {
            display: inline-block;
            padding: 0.5rem 1.25rem;
            background: var(--surface);
            border-radius: 100px;
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 1.5rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .section-title {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1.25rem;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }

        .section-description {
            font-size: 1.25rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }

        .features-container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 2rem;
        }

        .feature-card {
            background: var(--surface);
            padding: 2.5rem;
            border-radius: 16px;
            border: 1px solid var(--border-light);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--gradient-primary);
            transform: translateX(-100%);
            transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .feature-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.1);
            border-color: var(--primary-lighter);
            background: white;
        }

        .feature-card:hover::before {
            transform: translateX(0);
        }

        .feature-icon {
            width: 64px;
            height: 64px;
            background: white;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.75rem;
            margin-bottom: 1.75rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }

        .feature-card:hover .feature-icon {
            transform: scale(1.1) rotate(5deg);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }

        .feature-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: var(--text-primary);
            letter-spacing: -0.01em;
        }

        .feature-description {
            color: var(--text-secondary);
            line-height: 1.7;
            font-size: 1.05rem;
        }

        .process {
            padding: 120px 0;
            background: var(--surface);
            position: relative;
        }

        .process-timeline {
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
        }

        .process-steps {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 3rem;
            position: relative;
            z-index: 1;
        }

        .process-step {
            text-align: center;
        }

        .step-circle {
            width: 120px;
            height: 120px;
            background: white;
            border: 3px solid var(--primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            margin: 0 auto 2rem;
            position: relative;
            z-index: 2;
            box-shadow: 0 10px 30px -5px rgba(16, 185, 129, 0.2);
            transition: all 0.3s ease;
        }

        .process-step:nth-child(2) .step-circle,
        .process-step:nth-child(3) .step-circle {
            border-color: var(--border);
        }

        .process-step:hover .step-circle {
            transform: scale(1.1) rotate(10deg);
            border-color: var(--primary);
        }

        .step-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }

        .step-description {
            color: var(--text-secondary);
            line-height: 1.7;
            font-size: 1.05rem;
            max-width: 300px;
            margin: 0 auto;
        }

        .cta {
            padding: 120px 0;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            position: relative;
            overflow: hidden;
        }

        .cta::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
            animation: rotate 30s linear infinite;
        }

        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .cta-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 0 2rem;
            text-align: center;
            position: relative;
            z-index: 1;
        }

        .cta-title {
            font-size: 3.5rem;
            font-weight: 800;
            color: white;
            margin-bottom: 1.5rem;
            letter-spacing: -0.02em;
        }

        .cta-description {
            font-size: 1.375rem;
            color: rgba(255, 255, 255, 0.95);
            margin-bottom: 3rem;
            line-height: 1.6;
        }

        .cta-form {
            display: flex;
            gap: 1rem;
            max-width: 500px;
            margin: 0 auto;
        }

        .cta-input {
            flex: 1;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 1rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .cta-input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }

        .cta-input:focus {
            outline: none;
            border-color: white;
            background: rgba(255, 255, 255, 0.2);
        }

        .btn-white {
            background: white;
            color: var(--primary);
            padding: 1rem 2rem;
            border-radius: 10px;
            font-weight: 700;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.2);
            border: none;
            cursor: pointer;
        }

        .btn-white:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px -5px rgba(0, 0, 0, 0.3);
        }

        .footer {
            padding: 80px 0 40px;
            background: var(--text-primary);
            color: white;
        }

        .footer-container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .footer-content {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 4rem;
            margin-bottom: 4rem;
        }

        .footer-brand {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .footer-logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.75rem;
            font-weight: 700;
            color: white;
        }

        .footer-description {
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.7;
            font-size: 1.05rem;
        }

        .footer-column h4 {
            font-size: 1rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1.5rem;
            color: rgba(255, 255, 255, 0.95);
        }

        .footer-links {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .footer-link {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            font-size: 1rem;
            transition: color 0.3s ease;
            position: relative;
            padding-left: 0;
        }

        .footer-link:hover {
            color: white;
            padding-left: 5px;
        }

        .footer-bottom {
            padding-top: 3rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .footer-copyright {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.95rem;
        }

        .mobile-menu-toggle {
            display: none;
            flex-direction: column;
            gap: 4px;
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
        }

        .mobile-menu-toggle span {
            width: 24px;
            height: 2px;
            background: var(--text-primary);
            transition: all 0.3s ease;
            border-radius: 2px;
        }

        .reveal {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .reveal.active {
            opacity: 1;
            transform: translateY(0);
        }

        @media (max-width: 968px) {
            .hero-title {
                font-size: 3rem;
            }

            .features-grid,
            .tech-grid {
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            }

            .process-steps {
                grid-template-columns: 1fr;
                gap: 4rem;
            }

            .footer-content {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 640px) {
            .mobile-menu-toggle {
                display: flex;
            }

            .nav-menu,
            .nav-cta {
                display: none;
            }

            .hero-title {
                font-size: 2.25rem;
            }

            .hero-description {
                font-size: 1.125rem;
            }

            .hero-actions {
                flex-direction: column;
            }

            .features-grid {
                grid-template-columns: 1fr;
            }

            .footer-content {
                grid-template-columns: 1fr;
                text-align: center;
            }

            .footer-bottom {
                flex-direction: column;
                gap: 1rem;
            }

            .cta-form {
                flex-direction: column;
            }

            .section-title {
                font-size: 2.5rem;
            }
        }
      `}</style>

      {/* Navigation */}
      <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
        <div className="nav-container">
          <Link to="/" className="nav-logo">
            <img src={flavorLabIcon} alt="HealthLab" style={{ width: '42px', height: '42px', borderRadius: '12px' }} />
            <span>HealthLab</span>
          </Link>
          <ul className="nav-menu">
            <li><a href="#features" className="nav-link">Product</a></li>
            <li><a href="#process" className="nav-link">How It Works</a></li>
            <li><a href="#contact" className="nav-link">Contact</a></li>
          </ul>
          <div className="nav-cta">
            <Link to="/login" className="btn btn-secondary">Sign In</Link>
            <Link to="/signup" className="btn btn-primary">Get Early Access</Link>
          </div>
          <button className="mobile-menu-toggle">
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <div className="hero-badge">
              <span className="badge-new">NEW</span>
              AI-Powered Nutrition Platform Launching Soon
            </div>
            <h1 className="hero-title">
              The Future of<br />
              <span className="gradient-text">Nutrition Intelligence</span>
            </h1>
            <p className="hero-description">
              Transform your relationship with food through AI-driven insights, personalized nutrition planning, and intelligent health tracking.
            </p>
            <div className="hero-actions">
              <Link to="/signup" className="btn btn-primary btn-large">
                Request Early Access
              </Link>
              <Link to="/login" className="btn btn-secondary btn-large">
                View Demo
              </Link>
            </div>
          </div>

          {/* Product Preview */}
          <div className="product-preview">
            <div className="preview-container">
              <div className="browser-mockup">
                <div className="browser-header">
                  <div className="browser-dots">
                    <span className="browser-dot"></span>
                    <span className="browser-dot"></span>
                    <span className="browser-dot"></span>
                  </div>
                  <div className="browser-url">app.healthlab.io/dashboard</div>
                </div>
                <div className="dashboard-content">
                  {/* Dashboard Navigation Tabs */}
                  <div className="dashboard-nav">
                    <a href="#" className="dashboard-nav-item">
                      <span>🏠</span>
                      Dashboard
                    </a>
                    <a href="#" className="dashboard-nav-item">
                      <span>🧑‍🍳</span>
                      Recipe Generator
                    </a>
                    <a href="#" className="dashboard-nav-item">
                      <span>📋</span>
                      Meal Plans
                    </a>
                    <a href="#" className="dashboard-nav-item">
                      <span>🍽️</span>
                      Meal History
                    </a>
                    <a href="#" className="dashboard-nav-item">
                      <span>📖</span>
                      Journal
                    </a>
                  </div>

                  {/* Main Dashboard Content */}
                  <div className="dashboard-main">
                    {/* Daily Calories Card */}
                    <div className="calories-card">
                      <div className="calories-header">
                        <span className="calories-icon">⚡</span>
                        <h3 className="calories-title">Daily Calories</h3>
                      </div>
                      <div className="calories-progress">
                        <svg className="progress-ring" width="120" height="120">
                          <circle className="progress-ring-bg" cx="60" cy="60" r="45" />
                          <circle className="progress-ring-fill" cx="60" cy="60" r="45" />
                        </svg>
                        <div className="progress-text">
                          <div className="progress-percentage">6%</div>
                        </div>
                      </div>
                      <div className="calories-stats">
                        <div className="calorie-stat">
                          <span className="stat-label">Goal: 4000 kcal —</span>
                        </div>
                        <div className="calorie-stat">
                          <span className="stat-label">Consumed:</span>
                          <span className="stat-value">245 kcal</span>
                        </div>
                        <div className="calorie-stat">
                          <span className="stat-label">Remaining:</span>
                          <span className="stat-value">3755 kcal</span>
                        </div>
                      </div>
                      <button className="add-meal-btn">
                        <span>+</span>
                        Add Meal
                      </button>
                    </div>

                    {/* Macronutrients Card */}
                    <div className="macros-card">
                      <div className="macros-header">
                        <span className="macros-icon">🎯</span>
                        <h3 className="macros-title">Macronutrients</h3>
                      </div>
                      <div className="macro-item">
                        <div className="macro-header">
                          <span className="macro-name">Protein</span>
                          <span className="macro-values">6.0g / 300.0g</span>
                        </div>
                        <div className="macro-progress-bar">
                          <div className="macro-progress-fill protein"></div>
                        </div>
                      </div>
                      <div className="macro-item">
                        <div className="macro-header">
                          <span className="macro-name">Carbs</span>
                          <span className="macro-values">28.0g / 400.0g</span>
                        </div>
                        <div className="macro-progress-bar">
                          <div className="macro-progress-fill carbs"></div>
                        </div>
                      </div>
                      <div className="macro-item">
                        <div className="macro-header">
                          <span className="macro-name">Fat</span>
                          <span className="macro-values">13.0g / 133.3g</span>
                        </div>
                        <div className="macro-progress-bar">
                          <div className="macro-progress-fill fat"></div>
                        </div>
                      </div>
                      <div className="macro-item">
                        <div className="macro-header">
                          <span className="macro-name">Fiber</span>
                          <span className="macro-values">7.0g / 25.0g</span>
                        </div>
                        <div className="macro-progress-bar">
                          <div className="macro-progress-fill fiber"></div>
                        </div>
                      </div>
                    </div>

                    {/* Today's Activity Card */}
                    <div className="activity-card">
                      <div className="activity-header">
                        <span className="activity-icon">📈</span>
                        <h3 className="activity-title">Today's Activity</h3>
                      </div>
                      <div className="activity-item">
                        <div className="activity-left">
                          <div className="activity-item-icon">🍽️</div>
                          <div className="activity-info">
                            <div className="activity-label">Meals Logged</div>
                            <div className="activity-value">1 of 5 meals</div>
                            <div className="activity-sub">Avocado Toast • 1m ago</div>
                          </div>
                        </div>
                        <div className="activity-count">1</div>
                      </div>
                      <div className="activity-item">
                        <div className="activity-left">
                          <div className="activity-item-icon">💧</div>
                          <div className="activity-info">
                            <div className="activity-label">Water Intake</div>
                            <div className="activity-value">Goal: 2000ml</div>
                          </div>
                        </div>
                        <div className="activity-count">0<span style={{fontSize: '0.875rem', fontWeight: '500'}}>ml</span></div>
                      </div>
                      <div className="streak-badge">
                        <div className="streak-left">
                          <div className="streak-icon">💡</div>
                          <div className="streak-info">
                            <div className="streak-title">Streak</div>
                            <div className="streak-subtitle">Keep it going!</div>
                          </div>
                        </div>
                        <div className="streak-days">
                          <div className="streak-count">2</div>
                          <div className="streak-label">days</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <div className="section-header reveal">
          <div className="section-badge">Features</div>
          <h2 className="section-title">Powerful Nutrition Intelligence</h2>
          <p className="section-description">
            Advanced features designed to revolutionize how you understand and manage your nutrition.
          </p>
        </div>
        <div className="features-container">
          <div className="features-grid">
            <div className="feature-card reveal">
              <div className="feature-icon">🧠</div>
              <h3 className="feature-title">AI Meal Planning</h3>
              <p className="feature-description">
                Our advanced AI analyzes your preferences, health goals, and dietary restrictions to create perfectly balanced meal plans tailored specifically for you.
              </p>
            </div>
            <div className="feature-card reveal">
              <div className="feature-icon">📊</div>
              <h3 className="feature-title">Comprehensive Analytics</h3>
              <p className="feature-description">
                Track every aspect of your nutrition with detailed breakdowns of macros, micros, vitamins, and minerals. Visualize trends and patterns over time.
              </p>
            </div>
            <div className="feature-card reveal">
              <div className="feature-icon">🎯</div>
              <h3 className="feature-title">Goal-Driven Tracking</h3>
              <p className="feature-description">
                Set specific health objectives and receive real-time guidance on how your food choices impact your progress toward these goals.
              </p>
            </div>
            <div className="feature-card reveal">
              <div className="feature-icon">📅</div>
              <h3 className="feature-title">Calendar Tracker</h3>
              <p className="feature-description">
                Visualize your nutrition journey with our intuitive calendar view. Track meals, view patterns, and plan ahead with an interactive timeline of your health progress.
              </p>
            </div>
            <div className="feature-card reveal">
              <div className="feature-icon">🔬</div>
              <h3 className="feature-title">Science-Based Insights</h3>
              <p className="feature-description">
                Every recommendation is backed by peer-reviewed nutritional research, ensuring you receive evidence-based guidance for optimal health.
              </p>
            </div>
            <div className="feature-card reveal">
              <div className="feature-icon">🌿</div>
              <h3 className="feature-title">Apothecary (Coming Soon)</h3>
              <p className="feature-description">
                Discover natural remedies and supplements tailored to your nutritional needs. Get personalized recommendations for herbs, vitamins, and holistic wellness products.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="process" id="process">
        <div className="section-header reveal">
          <div className="section-badge">Process</div>
          <h2 className="section-title">Start Your Journey in Minutes</h2>
          <p className="section-description">
            Our streamlined onboarding process gets you up and running quickly.
          </p>
        </div>
        <div className="process-timeline">
          <div className="process-steps">
            <div className="process-step reveal">
              <div className="step-circle">📝</div>
              <h3 className="step-title">Create Profile</h3>
              <p className="step-description">
                Share your health goals, dietary preferences, and any restrictions. Takes less than 2 minutes.
              </p>
            </div>
            <div className="process-step reveal">
              <div className="step-circle">🎯</div>
              <h3 className="step-title">Set Goals</h3>
              <p className="step-description">
                Define what you want to achieve - weight management, energy boost, or specific health improvements.
              </p>
            </div>
            <div className="process-step reveal">
              <div className="step-circle">🚀</div>
              <h3 className="step-title">Start Tracking</h3>
              <p className="step-description">
                Begin logging meals and receive instant AI-powered insights and personalized recommendations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta" id="contact">
        <div className="cta-container">
          <h2 className="cta-title">Be Among the First</h2>
          <p className="cta-description">
            Join the waitlist for early access to HealthLab and revolutionize your approach to nutrition.
          </p>
          <form className="cta-form" onSubmit={handleFormSubmit}>
            <input type="email" className="cta-input" placeholder="Enter your email" required />
            <button type="submit" className="btn-white">Get Early Access</button>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-content">
            <div className="footer-brand">
              <div className="footer-logo">
                <img src={flavorLabIcon} alt="HealthLab" style={{ width: '42px', height: '42px', borderRadius: '12px' }} />
                <span>HealthLab</span>
              </div>
              <p className="footer-description">
                Pioneering the future of personalized nutrition through artificial intelligence and data-driven insights.
              </p>
            </div>
            <div className="footer-column">
              <h4>Product</h4>
              <div className="footer-links">
                <a href="#features" className="footer-link">Features</a>
                <a href="#" className="footer-link">Security</a>
                <a href="#" className="footer-link">Roadmap</a>
              </div>
            </div>
            <div className="footer-column">
              <h4>Company</h4>
              <div className="footer-links">
                <a href="#" className="footer-link">About</a>
                <a href="#" className="footer-link">Blog</a>
                <a href="#" className="footer-link">Careers</a>
                <a href="#" className="footer-link">Press Kit</a>
              </div>
            </div>
            <div className="footer-column">
              <h4>Support</h4>
              <div className="footer-links">
                <a href="#contact" className="footer-link">Contact</a>
                <a href="#" className="footer-link">FAQ</a>
                <a href="#" className="footer-link">Terms</a>
                <a href="#" className="footer-link">Privacy</a>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <div className="footer-copyright">
              © 2024 HealthLab. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

"""
frontend/app.py
AI Resume Screener — WENIFX-inspired Purple-Violet Dark UI
Deep midnight purple backgrounds · Neon violet glows · Glassmorphic cards
"""
from __future__ import annotations

import sys
import os
import json
import io
import time

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
load_dotenv(os.path.join(ROOT, ".env"))

from backend.pipeline import screen_resumes

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# PURPLE-VIOLET DARK THEME CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

/* ── Color Tokens ─────────────────────────────────────────── */
:root {
  --bg-void:      #060010;
  --bg-deep:      #0a0018;
  --bg-dark:      #0f0025;
  --bg-card:      rgba(18, 6, 42, 0.82);
  --bg-glass:     rgba(30, 10, 70, 0.55);
  --purple-900:   #1e0a3c;
  --purple-800:   #2d1067;
  --purple-700:   #4c1d95;
  --purple-600:   #6d28d9;
  --purple-500:   #7c3aed;
  --purple-400:   #8b5cf6;
  --purple-300:   #a78bfa;
  --purple-200:   #c4b5fd;
  --purple-100:   #ede9fe;
  --violet-glow:  #9333ea;
  --pink-accent:  #d946ef;
  --text-bright:  #f3e8ff;
  --text-mid:     #c4b5fd;
  --text-muted:   #7c5cbf;
  --text-dim:     #4a3570;
  --border-glow:  rgba(139,92,246,0.35);
  --border-dim:   rgba(109,40,217,0.18);
  --green:        #10b981;
  --amber:        #f59e0b;
  --red:          #ef4444;
}

/* ── Base ─────────────────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
  color: var(--text-bright);
}

/* ── Background — animated deep-purple void ─────────────── */
.stApp {
  background: var(--bg-void);
  min-height: 100vh;
  overflow-x: hidden;
}
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 55% at 15% 15%,  rgba(109,40,217,0.22) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 85% 75%,  rgba(147,51,234,0.18) 0%, transparent 55%),
    radial-gradient(ellipse 60% 50% at 50% 100%, rgba(76,29,149,0.14)  0%, transparent 50%),
    radial-gradient(ellipse 40% 60% at 90% 5%,   rgba(192,38,211,0.10) 0%, transparent 45%);
  animation: void-breathe 14s ease-in-out infinite alternate;
  pointer-events: none;
  z-index: 0;
}
@keyframes void-breathe {
  0%   { opacity: 0.7; transform: scale(1);    }
  50%  { opacity: 1;   transform: scale(1.05); }
  100% { opacity: 0.8; transform: scale(0.97); }
}

/* ── Floating neon orbs ─────────────────────────────────── */
.orb {
  position: fixed;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
}
.orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(109,40,217,0.28) 0%, transparent 70%);
  filter: blur(70px);
  top: -150px; left: -150px;
  animation: orb-drift 20s ease-in-out infinite;
}
.orb-2 {
  width: 380px; height: 380px;
  background: radial-gradient(circle, rgba(147,51,234,0.22) 0%, transparent 70%);
  filter: blur(60px);
  bottom: 5%; right: -100px;
  animation: orb-drift 25s ease-in-out infinite reverse 3s;
}
.orb-3 {
  width: 280px; height: 280px;
  background: radial-gradient(circle, rgba(192,38,211,0.18) 0%, transparent 70%);
  filter: blur(50px);
  top: 40%; left: 45%;
  animation: orb-drift 17s ease-in-out infinite 6s;
}
.orb-4 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(76,29,149,0.3) 0%, transparent 70%);
  filter: blur(40px);
  top: 70%; left: 15%;
  animation: orb-drift 22s ease-in-out infinite reverse 9s;
}
@keyframes orb-drift {
  0%, 100% { transform: translate(0px, 0px) scale(1); }
  25%       { transform: translate(25px,-30px) scale(1.08); }
  50%       { transform: translate(-15px,20px) scale(0.94); }
  75%       { transform: translate(30px, 10px) scale(1.04); }
}

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #080015 0%, #100020 50%, #0c001a 100%);
  border-right: 1px solid rgba(109,40,217,0.25);
}
[data-testid="stSidebar"]::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #7c3aed, #a855f7, #7c3aed, transparent);
  animation: top-bar-glow 4s linear infinite;
}
@keyframes top-bar-glow {
  0%   { opacity: 0.4; }
  50%  { opacity: 1; }
  100% { opacity: 0.4; }
}

/* ── Hero ────────────────────────────────────────────────── */
.hero-header {
  background: linear-gradient(135deg,
    rgba(76,29,149,0.3)  0%,
    rgba(109,40,217,0.2) 40%,
    rgba(147,51,234,0.15) 70%,
    rgba(192,38,211,0.1) 100%
  );
  border: 1px solid rgba(139,92,246,0.3);
  border-radius: 24px;
  padding: 3rem 4rem;
  margin-bottom: 2.2rem;
  backdrop-filter: blur(40px);
  position: relative;
  overflow: hidden;
  animation: hero-in 0.8s cubic-bezier(0.16,1,0.3,1) both;
  box-shadow:
    0 0 60px rgba(109,40,217,0.2),
    inset 0 1px 0 rgba(167,139,250,0.15);
}
@keyframes hero-in {
  from { opacity: 0; transform: translateY(-24px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Animated neon border */
.hero-header::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 25px;
  background: conic-gradient(
    from var(--angle, 0deg),
    transparent 20%,
    #7c3aed 40%,
    #a855f7 50%,
    #d946ef 60%,
    transparent 80%
  );
  animation: spin-border 6s linear infinite;
  z-index: -1;
  opacity: 0.6;
}
@keyframes spin-border {
  to { --angle: 360deg; }
}

/* Shimmer */
.hero-header::after {
  content: '';
  position: absolute;
  top: 0; left: -120%;
  width: 60%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(167,139,250,0.06), transparent);
  animation: hero-shimmer 6s ease-in-out infinite;
}
@keyframes hero-shimmer {
  0%   { left: -120%; }
  100% { left: 220%; }
}

/* Floating hex particles */
.hero-particles { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
.p-dot {
  position: absolute;
  border-radius: 50%;
  background: var(--purple-400);
  animation: rise linear infinite;
  opacity: 0;
}
@keyframes rise {
  0%   { transform: translateY(120%) scale(0); opacity: 0; }
  10%  { opacity: 0.8; }
  90%  { opacity: 0.6; }
  100% { transform: translateY(-200px) scale(1.2); opacity: 0; }
}

.hero-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 3.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #e9d5ff 0%, #c084fc 30%, #a855f7 60%, #7c3aed 100%);
  background-size: 250% 250%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  line-height: 1.1;
  animation: title-gradient 5s ease infinite, slide-in-left 0.8s ease both;
  position: relative;
  z-index: 2;
  text-shadow: none;
  filter: drop-shadow(0 0 30px rgba(168,85,247,0.4));
}
@keyframes title-gradient {
  0%,100% { background-position: 0% 50%; }
  50%      { background-position: 100% 50%; }
}
@keyframes slide-in-left {
  from { opacity: 0; transform: translateX(-30px); }
  to   { opacity: 1; transform: translateX(0); }
}

.hero-subtitle {
  color: var(--text-mid);
  font-size: 0.98rem;
  margin-top: 0.75rem;
  font-weight: 400;
  position: relative;
  z-index: 2;
  animation: fade-up 0.9s ease 0.3s both;
}

.pulse-dot {
  display: inline-block;
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #a855f7;
  box-shadow: 0 0 0 0 rgba(168,85,247,0.7);
  animation: pulse-ring 2s ease-in-out infinite;
  margin-right: 7px;
  vertical-align: middle;
}
@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 rgba(168,85,247,0.7); }
  70%  { box-shadow: 0 0 0 12px rgba(168,85,247,0); }
  100% { box-shadow: 0 0 0 0 rgba(168,85,247,0); }
}

/* ── Metric Cards ────────────────────────────────────────── */
.metric-row { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
.metric-card {
  flex: 1; min-width: 110px;
  background: var(--bg-card);
  border: 1px solid var(--border-dim);
  border-radius: 18px;
  padding: 1.4rem 1rem;
  backdrop-filter: blur(30px);
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1),
              border-color 0.3s,
              box-shadow 0.3s;
  animation: card-pop 0.6s cubic-bezier(0.34,1.56,0.64,1) both;
  cursor: default;
}
.metric-card::before {
  content: '';
  position: absolute;
  top: 0; left: -100%; width: 100%; height: 1.5px;
  background: linear-gradient(90deg, transparent, #a855f7, #d946ef, transparent);
  animation: top-scan 4s ease-in-out infinite;
}
@keyframes top-scan {
  0%   { left: -100%; }
  100% { left: 100%; }
}
.metric-card:hover {
  transform: translateY(-8px) scale(1.03);
  border-color: rgba(168,85,247,0.5);
  box-shadow: 0 20px 50px rgba(109,40,217,0.3), 0 0 0 1px rgba(168,85,247,0.1);
}
.metric-card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(168,85,247,0.08), transparent 70%);
  opacity: 0;
  transition: opacity 0.3s;
}
.metric-card:hover::after { opacity: 1; }

.metric-value {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2.4rem;
  font-weight: 800;
  background: linear-gradient(135deg, #e9d5ff, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: num-pop 0.7s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes num-pop {
  from { transform: scale(0.4) rotate(-5deg); opacity: 0; }
  to   { transform: scale(1) rotate(0deg);    opacity: 1; }
}
.metric-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 0.35rem;
}

/* ── Badges ──────────────────────────────────────────────── */
.badge-high {
  background: linear-gradient(135deg,#10b981,#059669);
  color:#fff; border-radius:30px; padding:4px 16px;
  font-weight:700; font-size:.75rem;
  box-shadow: 0 0 0 0 rgba(16,185,129,0.6);
  animation: badge-pulse-green 2.5s ease-in-out infinite;
}
@keyframes badge-pulse-green {
  0%,100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.6); }
  50%     { box-shadow: 0 0 16px 4px rgba(16,185,129,0.35); }
}
.badge-medium {
  background: linear-gradient(135deg,#d97706,#b45309);
  color:#fff; border-radius:30px; padding:4px 16px;
  font-weight:700; font-size:.75rem;
  box-shadow: 0 0 12px rgba(217,119,6,0.35);
}
.badge-low {
  background: linear-gradient(135deg,#dc2626,#b91c1c);
  color:#fff; border-radius:30px; padding:4px 16px;
  font-weight:700; font-size:.75rem;
  box-shadow: 0 0 12px rgba(220,38,38,0.3);
}

/* ── Candidate Cards ─────────────────────────────────────── */
.candidate-card {
  background: var(--bg-card);
  border: 1px solid var(--border-dim);
  border-radius: 20px;
  padding: 1.8rem 2.2rem;
  margin-bottom: 1.4rem;
  backdrop-filter: blur(35px);
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s, transform 0.35s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.3s;
  animation: card-rise 0.55s cubic-bezier(0.16,1,0.3,1) both;
  box-shadow: 0 4px 24px rgba(0,0,0,0.5);
}

/* Purple left accent bar */
.candidate-card::before {
  content: '';
  position: absolute;
  left: 0; top: 20%; bottom: 20%;
  width: 3px;
  background: linear-gradient(180deg, transparent, #7c3aed, #a855f7, #d946ef, transparent);
  border-radius: 0 3px 3px 0;
  opacity: 0;
  transition: opacity 0.3s, top 0.3s, bottom 0.3s;
}

/* Top glow line */
.candidate-card::after {
  content: '';
  position: absolute;
  top: 0; left: 15%; right: 15%; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(168,85,247,0.7), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}
.candidate-card:hover::before { opacity: 1; top: 10%; bottom: 10%; }
.candidate-card:hover::after  { opacity: 1; }
.candidate-card:hover {
  border-color: rgba(139,92,246,0.5);
  transform: translateY(-5px);
  box-shadow:
    0 24px 50px rgba(0,0,0,0.5),
    0 0 0 1px rgba(139,92,246,0.12),
    0 0 40px rgba(109,40,217,0.15);
}
@keyframes card-rise {
  from { opacity: 0; transform: translateY(22px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.card-rank {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1rem; font-weight: 800;
  color: #c084fc;
  background: rgba(124,58,237,0.18);
  border: 1px solid rgba(168,85,247,0.35);
  border-radius: 50%;
  width: 40px; height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1),
              background 0.3s, box-shadow 0.3s;
}
.candidate-card:hover .card-rank {
  transform: rotate(15deg) scale(1.2);
  background: rgba(168,85,247,0.3);
  box-shadow: 0 0 16px rgba(168,85,247,0.5);
}
.card-name {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.2rem; font-weight: 700;
  color: var(--text-bright);
}
.card-email { font-size: 0.78rem; color: var(--text-dim); }

.score-circle {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2.4rem; font-weight: 900;
  animation: score-spring 0.7s cubic-bezier(0.34,1.56,0.64,1) both;
  filter: drop-shadow(0 0 8px currentColor);
}
@keyframes score-spring {
  from { transform: scale(0) rotate(-10deg); opacity: 0; }
  to   { transform: scale(1) rotate(0deg);   opacity: 1; }
}
.score-label {
  font-size: 0.62rem; color: var(--text-dim);
  text-transform: uppercase; letter-spacing: .1em;
}

/* Skill tags */
.skill-tag {
  display: inline-block;
  background: rgba(109,40,217,0.15);
  border: 1px solid rgba(124,58,237,0.3);
  color: var(--purple-300);
  border-radius: 20px;
  padding: 3px 12px;
  font-size: 0.7rem;
  margin: 2px 3px;
  transition: all 0.22s cubic-bezier(0.34,1.56,0.64,1);
  cursor: default;
}
.skill-tag:hover {
  background: rgba(168,85,247,0.28);
  border-color: rgba(168,85,247,0.6);
  transform: translateY(-2px) scale(1.07);
  box-shadow: 0 4px 14px rgba(168,85,247,0.3);
  color: #e9d5ff;
}
.matched-tag {
  background: rgba(16,185,129,0.12);
  border-color: rgba(16,185,129,0.3);
  color: #6ee7b7;
}
.matched-tag:hover {
  background: rgba(16,185,129,0.25);
  box-shadow: 0 4px 14px rgba(16,185,129,0.3);
}

/* Explanation box */
.explanation-box {
  background: rgba(6, 0, 18, 0.9);
  border-left: 3px solid #7c3aed;
  border-radius: 0 14px 14px 0;
  padding: 1.2rem 1.4rem;
  margin-top: 1rem;
  font-size: 0.87rem;
  color: var(--text-mid);
  line-height: 1.65;
  position: relative;
  box-shadow: inset 0 0 30px rgba(109,40,217,0.06);
  animation: fade-up 0.4s ease both;
}
.explanation-box::before {
  content: '"';
  position: absolute;
  top: -12px; left: 10px;
  font-size: 5rem;
  color: rgba(124,58,237,0.1);
  font-family: Georgia, serif;
  pointer-events: none;
  line-height: 1;
}

/* Score bars */
.bar-track {
  background: rgba(30,10,60,0.8);
  border-radius: 6px; height: 7px;
  overflow: hidden; position: relative;
}
.bar-fill {
  height: 100%; border-radius: 6px;
  position: relative; overflow: hidden;
  transition: width 1.4s cubic-bezier(0.16,1,0.3,1);
}
.bar-fill::after {
  content: '';
  position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.35), transparent);
  animation: bar-shine 2.2s ease-in-out infinite;
}
@keyframes bar-shine {
  0%   { left: -100%; }
  100% { left: 200%; }
}

/* Section titles */
.section-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.2rem; font-weight: 700;
  color: var(--text-bright);
  margin: 1.8rem 0 1rem;
  display: flex; align-items: center; gap: 0.5rem;
}
.section-title::after {
  content: '';
  flex: 1; height: 1px;
  background: linear-gradient(90deg, rgba(124,58,237,0.6), transparent);
  margin-left: 0.6rem;
  animation: line-expand 0.8s ease both;
}
@keyframes line-expand {
  from { transform: scaleX(0); transform-origin: left; }
  to   { transform: scaleX(1); }
}

/* Sidebar steps */
.sidebar-step {
  background: rgba(109,40,217,0.07);
  border: 1px solid rgba(109,40,217,0.18);
  border-radius: 12px;
  padding: 0.9rem 1.1rem;
  margin-bottom: 0.65rem;
  transition: all 0.25s ease;
}
.sidebar-step:hover {
  background: rgba(124,58,237,0.14);
  border-color: rgba(168,85,247,0.4);
  transform: translateX(4px);
  box-shadow: 0 0 20px rgba(109,40,217,0.15);
}
.sidebar-step-num {
  font-size: 0.6rem; font-weight: 800;
  color: #a855f7;
  text-transform: uppercase; letter-spacing: 0.12em;
}
.sidebar-step-title {
  font-size: 0.84rem; font-weight: 600;
  color: var(--text-bright); margin-top: 0.1rem;
}

/* Buttons */
.stButton > button {
  background: linear-gradient(135deg, #7c3aed 0%, #a855f7 60%, #d946ef 100%);
  background-size: 200% 200%;
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 0.7rem 2rem;
  font-weight: 700;
  font-size: 0.95rem;
  width: 100%;
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  position: relative; overflow: hidden;
  animation: btn-gradient 4s ease infinite;
}
@keyframes btn-gradient {
  0%,100% { background-position: 0% 50%; }
  50%     { background-position: 100% 50%; }
}
.stButton > button::before {
  content: '';
  position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.45s ease;
}
.stButton > button:hover::before { left: 100%; }
.stButton > button:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 12px 35px rgba(124,58,237,0.55), 0 0 0 2px rgba(168,85,247,0.25);
}
.stButton > button:active { transform: scale(0.97); }

/* Progress bar */
.stProgress > div > div > div {
  background: linear-gradient(90deg, #6d28d9, #a855f7, #d946ef, #a855f7, #6d28d9);
  background-size: 300% 100%;
  border-radius: 6px;
  animation: pg-move 2s linear infinite;
}
@keyframes pg-move {
  0%   { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(15, 4, 35, 0.8);
  border-radius: 14px; padding: 5px;
  border: 1px solid rgba(109,40,217,0.15);
  gap: 4px;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 10px; color: var(--text-muted);
  font-weight: 500; transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg,rgba(109,40,217,0.3),rgba(168,85,247,0.2)) !important;
  color: #c084fc !important;
  box-shadow: 0 0 25px rgba(124,58,237,0.25);
}

/* Expander */
div[data-testid="stExpander"] {
  background: rgba(10,2,25,0.7);
  border: 1px solid rgba(109,40,217,0.12);
  border-radius: 14px;
  transition: border-color 0.25s;
}
div[data-testid="stExpander"]:hover {
  border-color: rgba(168,85,247,0.3);
}

/* Plotly frames */
[data-testid="stPlotlyChart"] {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(109,40,217,0.15);
  box-shadow: 0 4px 24px rgba(0,0,0,0.4);
  animation: fade-up 0.5s ease both;
}

/* Download buttons */
.stDownloadButton > button {
  background: rgba(109,40,217,0.12);
  border: 1px solid rgba(124,58,237,0.35);
  color: #c084fc;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.25s ease;
}
.stDownloadButton > button:hover {
  background: rgba(124,58,237,0.25);
  border-color: rgba(168,85,247,0.6);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(109,40,217,0.35);
}

/* JD info box */
.jd-box {
  background: rgba(6, 0, 18, 0.85);
  border: 1px solid rgba(109,40,217,0.2);
  border-radius: 16px;
  padding: 1.3rem 1.5rem;
  animation: fade-in 0.5s ease;
}
.jd-label {
  color: var(--text-dim);
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 0.75rem 0 0.35rem;
}
.jd-label:first-child { margin-top: 0; }

/* Feature cards (empty state) */
.feat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-dim);
  border-radius: 18px;
  padding: 1.6rem 1.8rem;
  text-align: center; flex: 1;
  transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1),
              border-color 0.3s, box-shadow 0.3s;
  animation: card-pop 0.6s ease both;
  cursor: default;
  position: relative; overflow: hidden;
}
.feat-card::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(124,58,237,0.12), transparent 70%);
  opacity: 0; transition: opacity 0.3s;
}
.feat-card:hover::before { opacity: 1; }
.feat-card:hover {
  transform: translateY(-8px) scale(1.04);
  border-color: rgba(168,85,247,0.45);
  box-shadow: 0 20px 50px rgba(109,40,217,0.3);
}
.feat-icon {
  font-size: 2.2rem;
  animation: icon-float 3s ease-in-out infinite;
  display: inline-block;
}
@keyframes icon-float {
  0%,100% { transform: translateY(0); }
  50%     { transform: translateY(-7px); }
}

/* Misc keyframes */
@keyframes card-pop {
  from { opacity: 0; transform: scale(0.9) translateY(15px); }
  to   { opacity: 1; transform: scale(1)   translateY(0); }
}
@keyframes fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* Hide Streamlit default chrome except sidebar toggle */
#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none !important; }
</style>

<!-- Floating orbs -->
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>
<div class="orb orb-4"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────
if "results"   not in st.session_state: st.session_state.results   = None
if "jd_fields" not in st.session_state: st.session_state.jd_fields = None
if "screened"  not in st.session_state: st.session_state.screened  = False

# ─────────────────────────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
  <div class="hero-particles">
    <div class="p-dot" style="width:5px;height:5px;left:8%; animation-duration:7s;animation-delay:0s;"></div>
    <div class="p-dot" style="width:3px;height:3px;left:20%;animation-duration:9s;animation-delay:1.2s;"></div>
    <div class="p-dot" style="width:4px;height:4px;left:35%;animation-duration:6s;animation-delay:0.5s;background:#d946ef"></div>
    <div class="p-dot" style="width:3px;height:3px;left:55%;animation-duration:8s;animation-delay:2s;"></div>
    <div class="p-dot" style="width:5px;height:5px;left:70%;animation-duration:10s;animation-delay:3s;background:#c084fc"></div>
    <div class="p-dot" style="width:2px;height:2px;left:82%;animation-duration:7.5s;animation-delay:1s;"></div>
    <div class="p-dot" style="width:4px;height:4px;left:92%;animation-duration:9s;animation-delay:4s;background:#a855f7"></div>
  </div>
  <div class="hero-title">🎯 AI Resume Screener</div>
  <div class="hero-subtitle">
    <span class="pulse-dot"></span>
    Powered by <strong style="color:#c084fc">Groq Llama 3.3-70B</strong> +
    Sentence-Transformers &nbsp;·&nbsp; Weighted Scoring &nbsp;·&nbsp; Natural-Language Explanations
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='font-family:Space Grotesk,sans-serif;font-weight:800;font-size:1.3rem;"
        "background:linear-gradient(135deg,#e9d5ff,#a855f7);-webkit-background-clip:text;"
        "-webkit-text-fill-color:transparent;margin-bottom:1.3rem;'>📁 Upload Files</h2>",
        unsafe_allow_html=True,
    )

    for num, title in [("Step 1","Upload Job Description"),("Step 2","Upload Resumes (up to 200)"),("Step 3","Configure & Run")]:
        st.markdown(f"<div class='sidebar-step'><div class='sidebar-step-num'>{num}</div><div class='sidebar-step-title'>{title}</div></div>", unsafe_allow_html=True)
        if num == "Step 1":
            jd_file = st.file_uploader("JD", type=["pdf","docx","txt"], label_visibility="collapsed", key="jd_upload")
        elif num == "Step 2":
            resume_files = st.file_uploader("Resumes", type=["pdf","docx"], accept_multiple_files=True, label_visibility="collapsed", key="resume_upload")

    with st.expander("⚙️ Scoring Weights", expanded=False):
        w_semantic = st.slider("Semantic Similarity", 0,100,40,key="w_sem") / 100
        w_skill    = st.slider("Skill Overlap",       0,100,35,key="w_sk")  / 100
        w_exp      = st.slider("Experience",          0,100,15,key="w_ex")  / 100
        w_edu      = st.slider("Education",           0,100,10,key="w_ed")  / 100
        ws = w_semantic+w_skill+w_exp+w_edu
        if abs(ws-1.0) > 0.01:
            st.warning(f"⚠️ Weights sum to {ws:.2f} (should be 1.0)")

    run_btn = st.button("🚀 Run Screening", type="primary")

    if st.session_state.screened:
        st.markdown(
            "<div style='margin-top:.8rem;background:rgba(16,185,129,0.08);"
            "border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:.7rem 1rem;"
            "color:#6ee7b7;font-weight:600;font-size:.82rem;text-align:center;'>"
            "<span class='pulse-dot' style='background:#10b981;box-shadow:0 0 0 0 rgba(16,185,129,0.6)'></span>"
            "Screening complete!</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div style='color:#4a3570;font-size:.7rem;text-align:center;line-height:1.8;'>"
        "🤖 Groq Llama 3.3-70B<br>🧠 all-MiniLM-L6-v2<br>⚡ FAISS Vector Search<br>"
        "🎨 Purple Void Theme</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# Run pipeline
# ─────────────────────────────────────────────────────────────────
if run_btn:
    if not jd_file:
        st.error("❌ Please upload a Job Description file.")
        st.stop()
    if not resume_files:
        st.error("❌ Please upload at least one resume.")
        st.stop()
    if len(resume_files) > 200:
        st.error("❌ Maximum 200 resumes allowed.")
        st.stop()
    api_key = os.environ.get("GROQ_API_KEY","")
    if not api_key or "placeholder" in api_key:
        st.error("❌ GROQ_API_KEY not set. Add your key to `ai_resume/.env` and restart.")
        st.stop()

    import backend.scorer as _scorer
    _scorer.WEIGHTS.update({"semantic":w_semantic,"skill":w_skill,"experience":w_exp,"education":w_edu})

    pb = st.progress(0, text="Initialising…")
    st_txt = st.empty()

    def progress_cb(msg:str, frac:float):
        pb.progress(max(0.0,min(1.0,frac)), text=msg)
        st_txt.markdown(f"<div style='color:#c084fc;font-size:.83rem;margin-top:.3rem'>{msg}</div>", unsafe_allow_html=True)

    with st.spinner(""):
        try:
            results = screen_resumes(
                jd_filename=jd_file.name, jd_bytes=jd_file.read(),
                resume_files=[(f.name, f.read()) for f in resume_files],
                progress_cb=progress_cb,
            )
            st.session_state.results   = results
            st.session_state.jd_fields = results[0]["jd_fields"] if results else {}
            st.session_state.screened  = True
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            st.stop()

    pb.progress(1.0, text="✅ Complete!")
    st_txt.empty()
    st.rerun()

# ─────────────────────────────────────────────────────────────────
# Results dashboard
# ─────────────────────────────────────────────────────────────────
if st.session_state.results:
    results   = st.session_state.results
    jd_fields = st.session_state.jd_fields or {}

    n   = len(results)
    nh  = sum(1 for r in results if r["confidence"]=="High")
    nm  = sum(1 for r in results if r["confidence"]=="Medium")
    nl  = sum(1 for r in results if r["confidence"]=="Low")
    avg = np.mean([r["total_score"] for r in results])
    top = max(r["total_score"] for r in results)

    # Metric row
    cards_html = ""
    for i,(val,col,lbl) in enumerate([
        (n,   "linear-gradient(135deg,#e9d5ff,#a855f7)", "📋 Screened"),
        (nh,  "linear-gradient(135deg,#6ee7b7,#10b981)", "🟢 Strong"),
        (nm,  "linear-gradient(135deg,#fde68a,#f59e0b)", "🟡 Medium"),
        (nl,  "linear-gradient(135deg,#fca5a5,#ef4444)", "🔴 Weak"),
        (f"{avg:.1f}", "linear-gradient(135deg,#e9d5ff,#a855f7)", "📊 Avg Score"),
        (f"{top:.1f}", "linear-gradient(135deg,#bfdbfe,#38bdf8)", "🏆 Top Score"),
    ]):
        cards_html += f"""
<div class="metric-card" style="animation-delay:{i*0.07}s">
  <div class="metric-value" style="background:{col};-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">{val}</div>
  <div class="metric-label">{lbl}</div>
</div>"""

    st.markdown(f"<div class='metric-row'>{cards_html}</div>", unsafe_allow_html=True)

    # Tabs
    t1,t2,t3,t4 = st.tabs(["📊 Overview","🃏 Candidates","📈 Analytics","📤 Export"])

    # ── Overview ──
    with t1:
        cl, cr = st.columns([2.2,1])
        with cl:
            st.markdown("<div class='section-title'>🏆 Ranked Candidates</div>", unsafe_allow_html=True)
            min_sc = st.slider("Min score filter",0,100,0,key="msf")
            filt   = [r for r in results if r["total_score"]>=min_sc]

            df = pd.DataFrame([{
                "Rank":r["rank"],"Name":r["name"],"Score":r["total_score"],
                "Confidence":r["confidence"],
                "Semantic%":r["breakdown"].get("semantic_similarity",0),
                "Skills%":r["breakdown"].get("skill_overlap",0),
                "Exp%":r["breakdown"].get("experience",0),
                "Edu%":r["breakdown"].get("education",0),
                "Exp(yrs)":r.get("resume_fields",{}).get("experience_years","?"),
                "Education":r.get("resume_fields",{}).get("education",""),
            } for r in filt])

            def cscore(v):
                if v>=70: return "background:rgba(16,185,129,0.15);color:#6ee7b7;font-weight:700"
                if v>=45: return "background:rgba(245,158,11,0.15);color:#fde68a;font-weight:700"
                return "background:rgba(239,68,68,0.15);color:#fca5a5;font-weight:700"

            st.dataframe(
                df.style.applymap(cscore,subset=["Score"])
                  .format({"Score":"{:.1f}","Semantic%":"{:.1f}","Skills%":"{:.1f}","Exp%":"{:.1f}","Edu%":"{:.1f}"}),
                use_container_width=True, hide_index=True)

        with cr:
            st.markdown("<div class='section-title'>📋 JD Requirements</div>", unsafe_allow_html=True)
            rs = jd_fields.get("required_skills",[])
            jh = "<div class='jd-box'>"
            if rs:
                jh += "<div class='jd-label'>Required Skills</div>"
                jh += "".join(f"<span class='skill-tag'>{s}</span>" for s in rs[:14])
            me = jd_fields.get("min_experience_years")
            jh += f"<div class='jd-label'>Experience</div><span style='color:#e9d5ff;font-weight:600'>{me or 'N/A'} yrs</span>"
            edu = jd_fields.get("education","")
            jh += f"<div class='jd-label'>Education</div><span style='color:#e9d5ff;font-weight:600'>{edu or 'N/A'}</span>"
            dom = jd_fields.get("domain","")
            if dom:
                jh += f"<div class='jd-label'>Domain</div><span style='color:#e9d5ff;font-weight:600'>{dom}</span>"
            jh += "</div>"
            st.markdown(jh, unsafe_allow_html=True)

    # ── Candidates ──
    with t2:
        st.markdown("<div class='section-title'>🃏 Candidate Profiles</div>", unsafe_allow_html=True)
        cf = st.multiselect("Filter confidence",["High","Medium","Low"],default=["High","Medium","Low"],key="cf2")
        jd_req = set(jd_fields.get("required_skills",[]))

        for idx,r in enumerate([x for x in results if x["confidence"] in cf]):
            conf = r["confidence"]
            bc   = {"High":"badge-high","Medium":"badge-medium","Low":"badge-low"}[conf]
            sc   = {"High":"#6ee7b7","Medium":"#fde68a","Low":"#fca5a5"}[conf]
            rf   = r.get("resume_fields",{})
            cs   = rf.get("skills",[])
            mat  = [s for s in cs if s in jd_req]
            unm  = [s for s in cs if s not in jd_req]

            sh = "".join(f"<span class='skill-tag matched-tag'>✓ {s}</span>" for s in mat[:8])
            sh += "".join(f"<span class='skill-tag'>{s}</span>" for s in unm[:6])

            st.markdown(f"""
<div class="candidate-card" style="animation-delay:{idx*0.06}s">
  <div style="display:flex;align-items:flex-start;gap:1rem;">
    <div style="flex:1">
      <div style="display:flex;align-items:center;gap:.75rem;flex-wrap:wrap;margin-bottom:.35rem">
        <span class="card-rank">#{r['rank']}</span>
        <span class="card-name">{r['name']}</span>
        <span class="{bc}">{conf}</span>
      </div>
      <div class="card-email">📧 {r.get('email','—') or '—'} &nbsp;·&nbsp; 💼 {rf.get('experience_years','?')} yrs &nbsp;·&nbsp; 🎓 {rf.get('education','—') or '—'}</div>
    </div>
    <div style="text-align:center;min-width:68px">
      <div class="score-circle" style="color:{sc}">{r['total_score']:.1f}</div>
      <div class="score-label">/ 100</div>
    </div>
  </div>
  <div style="margin-top:.9rem">{sh}</div>
</div>""", unsafe_allow_html=True)

            with st.expander(f"📊 Full analysis — {r['name']}"):
                ra,rb = st.columns([1,1])
                bd = r.get("breakdown",{})
                cats = ["Semantic","Skills","Experience","Education"]
                vals = [bd.get("semantic_similarity",0),bd.get("skill_overlap",0),bd.get("experience",0),bd.get("education",0)]

                with ra:
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=vals+[vals[0]], theta=cats+[cats[0]],
                        fill="toself",
                        fillcolor="rgba(124,58,237,0.18)",
                        line=dict(color="#a855f7",width=2.5),
                    ))
                    fig.update_layout(
                        polar=dict(
                            bgcolor="rgba(0,0,0,0)",
                            radialaxis=dict(visible=True,range=[0,100],
                                tickfont=dict(color="#4a3570",size=9),
                                gridcolor="rgba(109,40,217,0.15)",
                                linecolor="rgba(109,40,217,0.15)"),
                            angularaxis=dict(
                                tickfont=dict(color="#7c5cbf",size=11),
                                gridcolor="rgba(109,40,217,0.15)",
                                linecolor="rgba(109,40,217,0.15)"),
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#7c5cbf"),
                        margin=dict(t=20,b=20,l=20,r=20),
                        height=280, showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with rb:
                    exp_val = r.get("explanation")
                    if exp_val is None:
                        with st.spinner("⚡ Generating AI explanation on-demand…"):
                            try:
                                from backend.explainer import generate_explanation
                                exp_val = generate_explanation(
                                    r["jd_fields"],
                                    r["resume_fields"],
                                    r["score_dict"]
                                )
                                r["explanation"] = exp_val
                            except Exception as exc:
                                exp_val = f"Explanation generation failed: {exc}"
                                r["explanation"] = exp_val
                    st.markdown(f"<div class='explanation-box'>{exp_val}</div>", unsafe_allow_html=True)
                    for cat,val in zip(cats,vals):
                        bc2 = "#6ee7b7" if val>=70 else "#fde68a" if val>=45 else "#fca5a5"
                        bc3 = "#10b981" if val>=70 else "#f59e0b" if val>=45 else "#ef4444"
                        st.markdown(f"""
<div style="margin:.38rem 0">
  <div style="display:flex;justify-content:space-between;color:#7c5cbf;font-size:.73rem;margin-bottom:3px">
    <span>{cat}</span><span style="color:{bc2};font-weight:700">{val:.1f}%</span>
  </div>
  <div class="bar-track">
    <div class="bar-fill" style="width:{val}%;background:linear-gradient(90deg,{bc3}88,{bc3})"></div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Analytics ──
    with t3:
        st.markdown("<div class='section-title'>📈 Analytics Dashboard</div>", unsafe_allow_html=True)
        c1,c2 = st.columns([3,2])

        with c1:
            names  = [r["name"] for r in results]
            scores = [r["total_score"] for r in results]
            cols   = ["#6ee7b7" if r["confidence"]=="High" else "#fde68a" if r["confidence"]=="Medium" else "#fca5a5" for r in results]
            fig_b = go.Figure(go.Bar(
                x=scores,y=names,orientation="h",
                marker=dict(color=cols,opacity=0.88,
                    line=dict(color="rgba(168,85,247,0.2)",width=1)),
                text=[f"{s:.1f}" for s in scores],
                textposition="outside",
                textfont=dict(color="#c4b5fd",size=11),
            ))
            fig_b.update_layout(
                title=dict(text="🏆 Candidate Ranking",font=dict(color="#e9d5ff",size=14,family="Space Grotesk")),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(6,0,16,0.6)",
                xaxis=dict(range=[0,115],gridcolor="rgba(109,40,217,0.1)",
                    tickfont=dict(color="#4a3570"),title=dict(text="Score",font=dict(color="#4a3570"))),
                yaxis=dict(autorange="reversed",tickfont=dict(color="#7c5cbf")),
                font=dict(color="#7c5cbf"),
                margin=dict(t=50,b=20,l=10,r=70),
                height=max(320,n*44),
            )
            st.plotly_chart(fig_b, use_container_width=True)

        with c2:
            fig_p = go.Figure(go.Pie(
                labels=["High","Medium","Low"],values=[nh,nm,nl],
                marker=dict(colors=["#10b981","#f59e0b","#ef4444"],
                    line=dict(color="rgba(0,0,0,0.4)",width=2)),
                hole=0.62,textfont=dict(color="#e9d5ff"),
            ))
            fig_p.update_layout(
                title=dict(text="Confidence Split",font=dict(color="#e9d5ff",size=14,family="Space Grotesk")),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#7c5cbf"),
                margin=dict(t=50,b=0,l=0,r=0),height=340,
                legend=dict(font=dict(color="#7c5cbf"),bgcolor="rgba(0,0,0,0)"),
                annotations=[dict(text=f"<b>{n}</b>",x=0.5,y=0.5,showarrow=False,
                    font=dict(color="#c084fc",size=22,family="Space Grotesk"))]
            )
            st.plotly_chart(fig_p, use_container_width=True)

        st.markdown("<div class='section-title'>🔢 Score Breakdown</div>", unsafe_allow_html=True)
        bdf = pd.DataFrame([{
            "Candidate":r["name"],
            "Semantic":r["breakdown"].get("semantic_similarity",0)*0.40,
            "Skills":r["breakdown"].get("skill_overlap",0)*0.35,
            "Experience":r["breakdown"].get("experience",0)*0.15,
            "Education":r["breakdown"].get("education",0)*0.10,
        } for r in results])
        pal = {"Semantic":"#7c3aed","Skills":"#a855f7","Experience":"#d946ef","Education":"#ec4899"}
        fs = go.Figure()
        for col in ["Semantic","Skills","Experience","Education"]:
            fs.add_trace(go.Bar(name=col,x=bdf["Candidate"],y=bdf[col],
                marker_color=pal[col],marker_opacity=0.85))
        fs.update_layout(
            barmode="stack",paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(6,0,16,0.6)",
            xaxis=dict(tickfont=dict(color="#7c5cbf"),gridcolor="rgba(109,40,217,0.08)"),
            yaxis=dict(title="Weighted Contribution",tickfont=dict(color="#4a3570"),
                gridcolor="rgba(109,40,217,0.08)"),
            font=dict(color="#7c5cbf"),
            legend=dict(font=dict(color="#7c5cbf"),bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=20,b=20),height=340,
        )
        st.plotly_chart(fs, use_container_width=True)

    # ── Export ──
    with t4:
        st.markdown("<div class='section-title'>📤 Export Results</div>", unsafe_allow_html=True)
        edf = pd.DataFrame([{
            "Rank":r["rank"],"Name":r["name"],"Email":r.get("email",""),
            "Total Score":r["total_score"],"Confidence":r["confidence"],
            "Semantic%":r["breakdown"].get("semantic_similarity",0),
            "Skills%":r["breakdown"].get("skill_overlap",0),
            "Exp%":r["breakdown"].get("experience",0),
            "Edu%":r["breakdown"].get("education",0),
            "Exp(yrs)":r.get("resume_fields",{}).get("experience_years",""),
            "Education":r.get("resume_fields",{}).get("education",""),
            "Skills":", ".join(r.get("resume_fields",{}).get("skills",[])[:15]),
            "Explanation":r.get("explanation",""),
            "File":r.get("filename",""),
        } for r in results])
        ca,cb = st.columns(2)
        with ca:
            st.download_button("⬇️ Download CSV",
                edf.to_csv(index=False).encode("utf-8"),
                "resume_screening.csv","text/csv",use_container_width=True)
        with cb:
            payload={"jd":jd_fields,"results":[{k:v for k,v in r.items() if k!="jd_fields"} for r in results]}
            st.download_button("⬇️ Download JSON",
                json.dumps(payload,indent=2,default=str).encode("utf-8"),
                "resume_screening.json","application/json",use_container_width=True)
        st.markdown("<br/>",unsafe_allow_html=True)
        st.dataframe(edf,use_container_width=True,hide_index=True)

# ─────────────────────────────────────────────────────────────────
# Empty state
# ─────────────────────────────────────────────────────────────────
elif not run_btn:
    st.markdown("""
<div style="text-align:center;padding:4rem 2rem;">
  <div style="font-size:5rem;display:inline-block;animation:icon-float 2.5s ease-in-out infinite;
    filter:drop-shadow(0 0 20px rgba(168,85,247,0.6))">🎯</div>

  <div style="font-family:Space Grotesk,sans-serif;font-size:1.7rem;font-weight:800;
    background:linear-gradient(135deg,#e9d5ff,#c084fc,#a855f7);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;margin:1rem 0 .6rem">
    Ready to Screen Resumes
  </div>

  <div style="color:#4a3570;font-size:.92rem;max-width:520px;margin:0 auto;line-height:1.75">
    Upload your <strong style="color:#c084fc">Job Description</strong> and up to
    <strong style="color:#c084fc">200 Resumes</strong> in the sidebar,
    then click <strong style="color:#a855f7">🚀 Run Screening</strong> for AI-powered
    rankings, weighted scores, and natural-language explanations.
  </div>

  <div style="display:flex;justify-content:center;gap:1.2rem;margin-top:3rem;flex-wrap:wrap">
    <div class="feat-card" style="animation-delay:.1s;border-color:rgba(109,40,217,0.2)">
      <div class="feat-icon" style="animation-delay:0s">📄</div>
      <div style="color:#c084fc;font-weight:700;font-size:.9rem;margin-top:.6rem">Parse</div>
      <div style="color:#4a3570;font-size:.72rem;margin-top:.2rem">PDF · DOCX · TXT</div>
    </div>
    <div class="feat-card" style="animation-delay:.2s;border-color:rgba(147,51,234,0.2)">
      <div class="feat-icon" style="animation-delay:.6s">🤖</div>
      <div style="color:#c084fc;font-weight:700;font-size:.9rem;margin-top:.6rem">Extract</div>
      <div style="color:#4a3570;font-size:.72rem;margin-top:.2rem">Groq Llama 3.3</div>
    </div>
    <div class="feat-card" style="animation-delay:.3s;border-color:rgba(168,85,247,0.2)">
      <div class="feat-icon" style="animation-delay:1.2s">🧠</div>
      <div style="color:#a78bfa;font-weight:700;font-size:.9rem;margin-top:.6rem">Embed</div>
      <div style="color:#4a3570;font-size:.72rem;margin-top:.2rem">all-MiniLM-L6-v2</div>
    </div>
    <div class="feat-card" style="animation-delay:.4s;border-color:rgba(192,38,211,0.2)">
      <div class="feat-icon" style="animation-delay:1.8s">🏆</div>
      <div style="color:#e879f9;font-weight:700;font-size:.9rem;margin-top:.6rem">Rank</div>
      <div style="color:#4a3570;font-size:.72rem;margin-top:.2rem">Weighted Score</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

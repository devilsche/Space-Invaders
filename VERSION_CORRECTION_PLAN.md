# Version Correction Plan

## Problem
Multiple patch notes have incorrect version numbers and dates based on actual file creation timestamps.

## Current State (by file creation date)
1. **Oct 11, 16:32** - v1.3.0_2025-10-11_projectile-limit-weapon-tracking.md ✅ CORRECT
2. **Oct 11, 19:47** - v1.4.0_2025-10-11_missing-explosions-unicode-fix.md ✅ CORRECT
3. **Oct 14, 00:16** - v1.5.0_2025-10-13_custom-fonts-menu-polish.md ❌ DATE WRONG (should be 10-14)
4. **Oct 14, 02:22** - v1.3.0_2025-10-14_survivor-mode-ui-improvements.md ❌ VERSION WRONG (should be v1.6.0)
5. **Oct 14, 18:22** - v1.3.0_2025-01-14_shield-glow-system.md ❌ VERSION+DATE WRONG (should be v1.7.0_2025-10-14)
6. **Oct 15, 02:33** - v1.6.0_2025-10-15_try-again-and-fixes.md ❌ VERSION WRONG (should be v1.8.0)

## Proposed Corrections

### 1. Fix v1.5.0 Date
**Current:** `v1.5.0_2025-10-13_custom-fonts-menu-polish.md`
**New:** `v1.5.0_2025-10-14_custom-fonts-menu-polish.md`
**Reason:** File was actually created on Oct 14, 00:16

### 2. Rename v1.3.0 (Oct 14, 02:22) to v1.6.0
**Current:** `v1.3.0_2025-10-14_survivor-mode-ui-improvements.md`
**New:** `v1.6.0_2025-10-14_survivor-mode-ui-improvements.md`
**Reason:** Created after v1.4.0 and v1.5.0

### 3. Rename v1.3.0 (Oct 14, 18:22) to v1.7.0 and fix date
**Current:** `v1.3.0_2025-01-14_shield-glow-system.md`
**New:** `v1.7.0_2025-10-14_shield-glow-system.md`
**Reason:** Created after v1.6.0, date was January instead of October

### 4. Rename current v1.6.0 to v1.8.0
**Current:** `v1.6.0_2025-10-15_try-again-and-fixes.md`
**New:** `v1.8.0_2025-10-15_try-again-and-fixes.md`
**Reason:** Created after v1.7.0

## Final Chronological Order
1. v1.0.0 (Oct 07) - Initial Release
2. v1.1.0 (Oct 07) - EMP System Overhaul
3. v1.2.0 (Oct 07) - Menu System Overhaul
4. **v1.3.0 (Oct 11)** - Projectile Limit & Weapon Tracking ✅
5. **v1.4.0 (Oct 11)** - Missing Explosions & Unicode Fix ✅
6. **v1.5.0 (Oct 14)** - Custom Fonts & Menu Polish (fix date)
7. **v1.6.0 (Oct 14)** - Survivor Mode UI Improvements (rename)
8. **v1.7.0 (Oct 14)** - Shield Glow System (rename + fix date)
9. **v1.8.0 (Oct 15)** - Try Again Feature & Critical Fixes (rename)

## Action Required
Rename 4 files and update their internal version references.

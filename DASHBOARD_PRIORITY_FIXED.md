# ✅ Dashboard Priority: CSV First → DB Fallback

## 🔄 PERUBAHAN PRIORITAS

Dashboard sekarang **menurut desain Anda**: **CSV pertama, DB fallback**.

---

## 🎯 PRIORITAS BARU

### Before (Wrong)
```
Priority 1: Database ⭐ (dipakai jika ada data)
   ↓
Priority 2: CSV (fallback)
```

### After (Fixed) ✅
```
Priority 1: CSV ⭐ (dipakai jika file ada)
   ↓
Priority 2: Database (fallback jika CSV tidak ada)
```

---

## 📊 FLOW BARU

### Logic Flow
```python
1. Check if CSV exists
   csv_path = 'dashboard_ranking_data_multi.csv'
   
2. If CSV exists:
   → Load data from CSV ✅
   → Display stats & ranking
   
3. If CSV NOT exists:
   → Check Database
   → If DB has data: use DB
   → If DB empty: show empty state
```

---

## ✅ CODE CHANGES

### File: `scanner/views.py`

**Lines 106-210**: Completely restructured

**Old Logic**:
```python
# Check DB first
if summaries.count() == 0:
    # Load CSV
else:
    # Use DB
```

**New Logic**:
```python
# Check CSV first
if os.path.exists(csv_path):
    # Load CSV ✅
else:
    # Check DB
    if summaries.count() > 0:
        # Use DB
    else:
        # Empty state
```

---

## 📝 LOGGING

### CSV Loaded
```
INFO: Loading dashboard data from CSV file
```

### DB Fallback
```
INFO: CSV not found, falling back to Database
INFO: Loading X domain summaries from database
```

---

## 🎯 BENEFITS

### CSV Priority ✅
- ✅ **Static data** untuk display
- ✅ **Tidak depend** pada scan results
- ✅ **Easy to update** via file
- ✅ **Consistent** tampilan

### DB as Fallback ✅
- ✅ **Backup** data jika CSV hilang
- ✅ **Dynamic** dari scan results
- ✅ **Flexible** deployment

---

## 📊 USAGE SCENARIOS

### Scenario 1: CSV Available
```
File: dashboard_ranking_data_multi.csv exists
→ Load from CSV ✅
→ Display 135+ domains
→ Use CSV data for stats & ranking
```

### Scenario 2: CSV Missing, DB Available
```
File: dashboard_ranking_data_multi.csv NOT exists
→ Check Database ✅
→ If DB has data: use DB
→ Display scan results
```

### Scenario 3: Both Empty
```
File: CSV NOT exists
Database: Empty
→ Show empty state
→ No data message
```

---

## ✅ VERIFICATION

### Check Priority
```python
# In Django shell or logs
# Should see one of these:

"Loading dashboard data from CSV file"  ← CSV prioritized!

OR

"CSV not found, falling back to Database"  ← DB fallback
```

---

## 🚀 DEPLOYMENT

### File Required
```
dashboard_ranking_data_multi.csv
Location: Root project directory
```

### CSV Format
```csv
domain,jumlah_kasus,hack judol,hacked,pornografi,hack_judol,last_scan
example.com,42,0.0,0,42,0,2025-09-03 14:48:28
```

---

## 📝 SUMMARY

**Status**: ✅ **Fixed sesuai desain Anda!**

**Priority**:  
1. ✅ **CSV first** (dashboard_ranking_data_multi.csv)
2. ✅ **DB fallback** (DomainScanSummary)

**Result**: Dashboard akan **selalu pakai CSV** jika file ada! 🎉

---

**Selesai! Dashboard sesuai desain Anda!** ✨


# Research: Phase 2 - 提醒框优化

**Date:** 2026-04-22
**Researcher:** Claude
**Objective:** Answer "What do I need to know to PLAN this phase well?"

---

## 1. Current Implementation Analysis

### 1.1 Data Flow Architecture

```
爬虫写入文件
      ↓
FileWatcherService (watchdog)
      ↓ (file modified event, 200ms debounce)
on_file_change_callback() in main.py
      ↓
broadcast_platform_update(platform)  → DataUpdateMessage
broadcast_stats_update(platform)     → StatsUpdateMessage
      ↓
WebSocket ConnectionManager.broadcast()
      ↓
Frontend WSClient.handleMessage()
      ↓
DataNotification.show() / handleDataUpdate()
      ↓
通知弹窗显示
```

### 1.2 Key Components

#### Backend: `api/services/file_watcher.py`

- **Debounce mechanism**: 200ms timer per platform (`DEBOUNCE_SECONDS = 0.2`)
- **File size tracking**: Only triggers when file size **increases** (append detection)
- **Per-platform timers**: `_debounce_timers: Dict[str, threading.Timer]`
- **Two callbacks per file change**:
  1. `broadcast_platform_update(platform)` - platform-specific
  2. `broadcast_stats_update(platform)` - global stats

#### Backend: `api/main.py`

```python
async def on_file_change_callback(platform: str):
    # Broadcast platform-specific update
    await broadcast_platform_update(platform)
    # Broadcast global stats update  
    await broadcast_stats_update(platform)
```

**Critical Finding**: Each file change triggers **TWO** WebSocket messages.

#### Backend: `api/routers/websocket.py`

- `DataUpdateMessage`: `{type: "data_update", platform: str, timestamp: str}`
- `StatsUpdateMessage`: `{type: "stats_update", total_notes: int, total_images: int, timestamp: str}`
- `SubscriptionUpdateMessage`: `{type: "subscription_update", subscription_id, keyword, platform, new_count, timestamp}`

**Missing Fields**: No `new_count`, no content titles, no item details in the messages.

#### Frontend: `viewer/static/js/notifications.js`

```javascript
function showDataNotification(data) {
    // data: {platform, count, keyword, message, timestamp}
    const title = data.message || `📥 ${config.name} 新数据`;
    const detail = data.keyword
        ? `关键词: ${data.keyword}`
        : (data.count ? `新增 ${data.count} 条数据` : '数据已更新');
    
    // Auto-close after 5000ms
    const autoCloseTimeout = setTimeout(() => {
        closeNotification(notification);
    }, 5000);
}
```

**Current behavior**:
- Auto-close time: 5000ms (5 seconds) ✓
- No deduplication
- No content title display
- Count always shows same number from stats

#### Frontend: `viewer/static/js/app.js`

```javascript
window.WSClient.subscribe('xhs', (data) => {
    if (data.type === 'data_update') {
        window.DataNotification.handleDataUpdate(data);
    } else if (data.type === 'stats_update') {
        // Also shows notification for stats_update
        window.DataNotification.show({
            platform: 'xhs',
            count: data.total_notes || 0,
            message: '📊 数据统计已更新'
        });
    }
});
```

**Critical Finding**: For each file change:
1. `data_update` → `handleDataUpdate()` → shows notification
2. `stats_update` → `show()` → shows **another** notification

**This explains BUG-02**: Each file change causes **TWO notifications**!

---

## 2. Root Cause Analysis

### BUG-02: 修复提醒框一直弹出的问题

**Root Cause**: Multiple notification triggers per file change

1. **Dual callback**: `on_file_change_callback` calls both `broadcast_platform_update` AND `broadcast_stats_update`
2. **Double frontend handling**: Both message types trigger notification display
3. **No deduplication**: Frontend shows both notifications without checking if they're duplicates

**Evidence**:
- `main.py` line 56-58: Two broadcast calls
- `app.js` line 320-330: Two notification calls for same event

**Solution Options**:
1. **Backend dedup**: Only send one message type per file change
2. **Frontend dedup**: Use message deduplication based on timestamp/hash
3. **Hybrid**: Reduce messages from backend + add frontend guard

### BUG-03: 修复数据统计一直显示"新增 340 条数据"的问题

**Root Cause**: Count value comes from `total_notes` not `new_count`

```javascript
// notifications.js handleDataUpdate:
showDataNotification({
    count: data.new_count || 0,  // new_count is never provided!
});

// app.js stats_update handler:
window.DataNotification.show({
    count: data.total_notes || 0,  // Uses TOTAL notes, not new count!
});
```

**Evidence**:
- `DataUpdateMessage` schema has no `new_count` field
- `StatsUpdateMessage` has `total_notes` which is cumulative
- Frontend uses `total_notes` as count, showing the same number each time

**Solution**: Track incremental changes and send actual new count in messages.

---

## 3. Implementation Patterns for Requirements

### NOTIF-01: 提醒框显示更新的内容标题

**Current Gap**: Backend messages don't include content details.

**Implementation Pattern**:
1. When file changes, read the **newly appended** records
2. Extract titles from new records
3. Include titles in the broadcast message

**Technical Approach**:
```python
# In broadcast_platform_update or new function:
async def broadcast_platform_update_with_content(platform: str):
    # Read last N records from the file
    new_records = await get_recent_records(platform, limit=5)
    
    message = {
        "type": "data_update",
        "platform": platform,
        "new_count": len(new_records),
        "titles": [r.get("title", "") for r in new_records[:3]],
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(message)
```

**Files to modify**:
- `api/schemas/crawler.py`: Add `new_count`, `titles` to `DataUpdateMessage`
- `api/routers/websocket.py`: Modify `broadcast_platform_update`
- `api/routers/notes.py`: Add function to get recent records

### NOTIF-02: 提醒框维持时间延长

**Current State**: Already 5 seconds (line 154 in notifications.js)

**Assessment**: 5 seconds is within the target 3-5 second range. No change needed unless user wants longer.

**If needed**: Modify line 154:
```javascript
}, 5000);  // Change to 3000-5000 as desired
```

### NOTIF-03: 提醒框去重

**Implementation Pattern**: Content-based deduplication with time window

```javascript
// In notifications.js:
const recentNotifications = new Map(); // hash -> timestamp

function showDataNotification(data) {
    // Create hash from content
    const hash = `${data.platform}-${data.titles?.join(',') || data.count}`;
    
    // Check if recently shown (within 5 seconds)
    const lastShown = recentNotifications.get(hash);
    if (lastShown && Date.now() - lastShown < 5000) {
        console.log('[通知] 去重，跳过:', hash);
        return;
    }
    
    recentNotifications.set(hash, Date.now());
    
    // Clean old entries
    for (const [key, time] of recentNotifications) {
        if (Date.now() - time > 30000) recentNotifications.delete(key);
    }
    
    // ... rest of notification logic
}
```

---

## 4. Dependencies and Integration Points

### Backend Dependencies

| File | Purpose | Changes Needed |
|------|---------|----------------|
| `api/schemas/crawler.py` | Message schemas | Add `new_count`, `titles` fields |
| `api/routers/websocket.py` | Broadcast functions | Include content in messages |
| `api/routers/notes.py` | Data reading | Add `get_recent_records()` |
| `api/main.py` | Callback logic | Consider single message per event |

### Frontend Dependencies

| File | Purpose | Changes Needed |
|------|---------|----------------|
| `viewer/static/js/notifications.js` | Notification display | Add dedup, show titles |
| `viewer/static/js/app.js` | XHS WebSocket handler | Remove redundant `stats_update` notification |
| `viewer/static/js/douyin-app.js` | Douyin handler | Same pattern |
| `viewer/static/js/bilibili-app.js` | Bilibili handler | Same pattern |
| `viewer/static/js/zhihu-app.js` | Zhihu handler | Same pattern |

### Data Flow Dependencies

1. **File append detection**: Requires tracking file positions per platform
2. **New record extraction**: Need to read only newly added lines
3. **Title extraction**: Parse JSONL/JSON and extract title field

---

## 5. Recommended Approach

### Phase 2.1: Fix Duplicate Notifications (BUG-02)

**Priority: High | Complexity: Low**

**Steps**:
1. In `app.js` (and other platform handlers), remove the `stats_update` notification trigger
2. Keep `data_update` as the primary notification source
3. `stats_update` should only update the stats display, not trigger notifications

```javascript
// app.js - BEFORE:
} else if (data.type === 'stats_update') {
    window.DataNotification.show({...});  // REMOVE THIS
}

// app.js - AFTER:
} else if (data.type === 'stats_update') {
    // Only update stats display, no notification
    updateStatsDisplay(data);
}
```

### Phase 2.2: Add Deduplication (NOTIF-03)

**Priority: High | Complexity: Medium**

**Steps**:
1. Add deduplication Map in `notifications.js`
2. Hash based on `platform + titles + timestamp (minute granularity)`
3. Skip notification if same hash within 5 seconds

### Phase 2.3: Show Content Titles (NOTIF-01)

**Priority: Medium | Complexity: High**

**Steps**:
1. Add `new_count` and `titles` fields to `DataUpdateMessage` schema
2. Create `get_recent_records()` function in `notes.py`
3. Modify `broadcast_platform_update()` to include new records
4. Update frontend to display titles in notification

**Schema Update**:
```python
class DataUpdateMessage(BaseModel):
    type: str = "data_update"
    platform: str
    timestamp: str = ""
    new_count: int = 0           # NEW
    titles: List[str] = []       # NEW
```

### Phase 2.4: Fix Count Display (BUG-03)

**Priority: Medium | Complexity: Medium**

**Steps**:
1. Track previous total count per platform
2. Calculate delta: `new_count = current_total - previous_total`
3. Include `new_count` in the message

**Implementation**:
```python
# In file_watcher or websocket module:
_previous_counts: Dict[str, int] = {}

async def broadcast_platform_update(platform: str):
    current_count = await get_count_for_platform(platform)
    new_count = current_count - _previous_counts.get(platform, 0)
    _previous_counts[platform] = current_count
    
    message = DataUpdateMessage(
        platform=platform,
        new_count=max(0, new_count),
        ...
    )
```

### Phase 2.5: Display Time Adjustment (NOTIF-02)

**Priority: Low | Complexity: Low**

**Steps**:
1. Verify current 5-second display time meets requirements
2. If user wants longer, adjust `notifications.js` line 154

---

## 6. Validation Strategy

### For BUG-02 (Duplicate Notifications)

**Test Case**:
1. Start crawler, observe notifications
2. Each data file change should produce **exactly one** notification
3. Verify via console logs that only one `showDataNotification` call per event

**Verification**:
```javascript
// Add counter for debugging
let notificationCount = 0;
function showDataNotification(data) {
    notificationCount++;
    console.log(`[通知] 第 ${notificationCount} 次`, data);
    // ...
}
```

### For BUG-03 (Fixed Count Display)

**Test Case**:
1. Note current total: e.g., 340 notes
2. Trigger crawler to add 5 new notes
3. Notification should show "新增 5 条数据" not "新增 345 条数据"

**Verification**:
- Check `new_count` field in WebSocket message
- Verify delta calculation is correct

### For NOTIF-01 (Content Titles)

**Test Case**:
1. Add new data with specific titles
2. Notification should show the titles, e.g., "标题1, 标题2, 等3条"
3. Click notification should be possible (future enhancement)

**Verification**:
- Check `titles` array in WebSocket message
- Verify frontend displays titles correctly

### For NOTIF-03 (Deduplication)

**Test Case**:
1. Rapid file changes (multiple writes within 1 second)
2. Should only show one notification
3. Different content should still show new notification

**Verification**:
```javascript
// Test dedup
showDataNotification({platform: 'xhs', titles: ['A']});  // Shows
showDataNotification({platform: 'xhs', titles: ['A']});  // Skipped
showDataNotification({platform: 'xhs', titles: ['B']});  // Shows
```

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing notification flow | Medium | High | Test all platforms after changes |
| Performance impact from reading files | Low | Medium | Limit to last 5 records |
| Race condition in count tracking | Low | Medium | Use proper locking |
| Frontend memory leak in dedup Map | Low | Low | Implement cleanup of old entries |

---

## 8. Open Questions

1. **How many titles to show?** - Recommendation: 3 titles max, with "...等N条" suffix
2. **Notification click behavior?** - Future enhancement (ENH-01), not in this phase
3. **Cross-platform notification grouping?** - Future consideration
4. **Should stats_update still be sent?** - Yes, for stats display, but not for notification

---

## RESEARCH COMPLETE

**Summary**: 
- Root cause of duplicate notifications identified: dual message types triggering same notification
- Root cause of fixed count identified: using total instead of delta
- Implementation patterns defined for all requirements
- Dependencies and integration points mapped
- Validation strategy established

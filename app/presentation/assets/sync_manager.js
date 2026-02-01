/**
 * SIWES Logbook Sync Manager
 * Handles IndexedDB storage for offline logs and synchronization with the server.
 */

class SyncManager {
    constructor() {
        this.dbName = 'siwes_db';
        this.storeName = 'daily_logs';
        this.version = 1;
        this.db = null;
    }

    /**
     * Initialize IndexedDB connection
     */
    async init() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);

            request.onerror = (event) => {
                console.error("IndexedDB error:", event.target.error);
                reject(event.target.error);
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                console.log("IndexedDB initialized");
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    // Create object store with client_uuid as key
                    const store = db.createObjectStore(this.storeName, { keyPath: 'client_uuid' });
                    // Indexes for searching
                    store.createIndex('status', 'status', { unique: false });
                    store.createIndex('log_date', 'log_date', { unique: false });
                    store.createIndex('synced', 'synced', { unique: false });
                    console.log("Object store created");
                }
            };
        });
    }

    /**
     * Save a log entry to IndexedDB
     * @param {Object} logData - The log entry data
     * @returns {Promise<string>} - The client_uuid of the saved log
     */
    async saveLog(logData) {
        if (!this.db) await this.init();

        // Ensure UUID exists
        if (!logData.client_uuid) {
            logData.client_uuid = crypto.randomUUID();
        }

        // Default flags
        if (logData.synced === undefined) logData.synced = false;
        logData.updated_at = new Date().toISOString();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.put(logData);

            request.onsuccess = () => {
                console.log(`Log saved locally: ${logData.client_uuid}`);
                // Dispatch event for UI updates
                window.dispatchEvent(new CustomEvent('log-saved', { detail: logData }));
                resolve(logData.client_uuid);
            };

            request.onerror = (e) => reject(e.target.error);
        });
    }

    /**
     * Get all logs that haven't been synced yet
     * @returns {Promise<Array>}
     */
    async getUnsyncedLogs() {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const index = store.index('synced');
            // Get all records where synced is 0/false
            const request = index.getAll(IDBKeyRange.only(false));

            request.onsuccess = () => resolve(request.result);
            request.onerror = (e) => reject(e.target.error);
        });
    }

    /**
     * Attempt to sync unsynced logs to the server
     * @returns {Promise<number>} - Count of successfully synced logs
     */
    async syncWithServer() {
        const logs = await this.getUnsyncedLogs();
        if (logs.length === 0) return 0;

        console.log(`Found ${logs.length} logs to sync...`);
        let syncedCount = 0;

        for (const log of logs) {
            try {
                // Prepare payload (match SyncService expectation)
                const payload = {
                    client_uuid: log.client_uuid,
                    log_date: log.log_date,
                    week_number: parseInt(log.week_number),
                    activity_description: log.activity_description,
                    latitude: log.latitude,
                    longitude: log.longitude
                };

                // Send to server
                const response = await fetch('/student/logbook/sync', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        // Add X-CSRF-Token if needed, or rely on cookie
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    // Mark as synced
                    log.synced = true;
                    log.synced_at = new Date().toISOString();
                    await this.saveLog(log);
                    syncedCount++;
                    console.log(`Synced log: ${log.client_uuid}`);
                } else {
                    console.error(`Failed to sync log ${log.client_uuid}:`, response.statusText);
                }
            } catch (err) {
                console.error(`Network error syncing log ${log.client_uuid}:`, err);
            }
        }

        if (syncedCount > 0) {
            window.dispatchEvent(new CustomEvent('sync-complete', { detail: { count: syncedCount } }));
            // Optional: Reload page to show new server state?
            // window.location.reload(); 
        }

        return syncedCount;
    }
}

// Global instance
window.syncManager = new SyncManager();

// Initialize on load
window.addEventListener('load', () => {
    window.syncManager.init().catch(console.error);
});

// Network status listeners
window.addEventListener('online', () => {
    console.log("Online detected: Attempting sync...");
    window.syncManager.syncWithServer();
    updateNetworkStatus(true);
});

window.addEventListener('offline', () => {
    console.log("Offline detected.");
    updateNetworkStatus(false);
});

function updateNetworkStatus(isOnline) {
    const badge = document.getElementById('network-status-badge');
    if (badge) {
        if (isOnline) {
            badge.className = 'badge bg-success-subtle text-success-emphasis rounded-pill';
            badge.innerHTML = '<i class="bi bi-wifi"></i> Online';
        } else {
            badge.className = 'badge bg-warning-subtle text-warning-emphasis rounded-pill';
            badge.innerHTML = '<i class="bi bi-wifi-off"></i> Offline';
        }
    }
}

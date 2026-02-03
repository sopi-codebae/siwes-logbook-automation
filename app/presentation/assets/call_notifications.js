// SSE Notification Listener for Call Notifications
(function () {
    let eventSource = null;
    let currentCallId = null;

    function initializeSSE() {
        // Connect to SSE stream
        eventSource = new EventSource('/notifications/stream');

        eventSource.onopen = function () {
            console.log('[SSE] Connected to notification stream');
        };

        eventSource.onmessage = function (event) {
            try {
                const data = JSON.parse(event.data);
                console.log('[SSE] Received event:', data);

                // Handle different event types
                switch (data.type) {
                    case 'connected':
                        console.log('[SSE] Connection confirmed for user:', data.user_id);
                        break;

                    case 'call_incoming':
                        handleIncomingCall(data);
                        break;

                    case 'call_cancelled':
                        handleCallCancelled(data);
                        break;

                    case 'call_accepted':
                        handleCallAccepted(data);
                        break;
                }
            } catch (error) {
                console.error('[SSE] Error parsing event:', error);
            }
        };

        eventSource.onerror = function (error) {
            console.error('[SSE] Connection error:', error);
            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
                console.log('[SSE] Attempting to reconnect...');
                eventSource.close();
                initializeSSE();
            }, 5000);
        };
    }

    function handleIncomingCall(data) {
        console.log('[CALL] Incoming call from:', data.caller_name);

        // Store call ID for accept/decline actions
        currentCallId = data.call_id;

        // Get modal elements
        const modal = document.getElementById('call-notification-modal');
        const backdrop = document.getElementById('call-notification-backdrop');
        const callerName = document.getElementById('caller-name');
        const callerInitials = document.getElementById('caller-initials');
        const callTypeText = document.getElementById('call-type-text');

        // Update modal content
        callerName.textContent = data.caller_name;

        // Generate initials
        const nameParts = data.caller_name.split(' ');
        const initials = nameParts.map(p => p[0]).join('').substring(0, 2).toUpperCase();
        callerInitials.textContent = initials;

        // Set call type
        const callTypeIcon = data.call_type === 'video' ? 'camera-video' : 'telephone';
        callTypeText.textContent = data.call_type === 'video' ? 'Video Call' : 'Voice Call';

        // Show modal
        modal.style.display = 'block';
        backdrop.style.display = 'block';
        setTimeout(() => {
            modal.classList.add('show');
            backdrop.classList.add('show');
        }, 10);

        // Play notification sound (optional)
        playNotificationSound();
    }

    function handleCallCancelled(data) {
        console.log('[CALL] Call cancelled');
        hideCallModal();
    }

    function handleCallAccepted(data) {
        console.log('[CALL] Call accepted, redirecting...');
        window.location.href = data.redirect_url;
    }

    function hideCallModal() {
        const modal = document.getElementById('call-notification-modal');
        const backdrop = document.getElementById('call-notification-backdrop');

        modal.classList.remove('show');
        backdrop.classList.remove('show');

        setTimeout(() => {
            modal.style.display = 'none';
            backdrop.style.display = 'none';
        }, 300);

        currentCallId = null;
    }

    function playNotificationSound() {
        // Create and play a simple notification beep
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            gainNode.gain.value = 0.3;

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.2);
        } catch (error) {
            console.log('[AUDIO] Could not play notification sound:', error);
        }
    }

    // Accept call button handler
    document.addEventListener('DOMContentLoaded', function () {
        const acceptBtn = document.getElementById('accept-call-btn');
        const declineBtn = document.getElementById('decline-call-btn');

        if (acceptBtn) {
            acceptBtn.addEventListener('click', function () {
                if (!currentCallId) return;

                fetch(`/api/calls/${currentCallId}/accept`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.href = data.redirect_url;
                        } else {
                            alert('Failed to accept call: ' + (data.error || 'Unknown error'));
                            hideCallModal();
                        }
                    })
                    .catch(error => {
                        console.error('Error accepting call:', error);
                        alert('Failed to accept call. Please try again.');
                        hideCallModal();
                    });
            });
        }

        if (declineBtn) {
            declineBtn.addEventListener('click', function () {
                if (!currentCallId) return;

                fetch(`/api/calls/${currentCallId}/decline`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                    .then(response => response.json())
                    .then(data => {
                        hideCallModal();
                        if (!data.success) {
                            console.error('Failed to decline call:', data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error declining call:', error);
                        hideCallModal();
                    });
            });
        }

        // Initialize SSE connection
        initializeSSE();
    });
})();

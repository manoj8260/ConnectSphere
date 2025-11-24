        document.addEventListener('DOMContentLoaded', () => {
            // --- Modal Handling ---
            const modalTriggers = document.querySelectorAll('[data-modal-target]');
            const closeButtons = document.querySelectorAll('.close-btn');
            const modalOverlays = document.querySelectorAll('.modal-overlay');

            // Function to open a modal
            const openModal = (modalId) => {
                const modal = document.getElementById(modalId);
                if (modal) {
                    modal.classList.add('active');
                }
            };

            // Function to close any active modal
            const closeModal = () => {
                document.querySelector('.modal-overlay.active')?.classList.remove('active');
            };

            // Add click listeners to all modal triggers
            modalTriggers.forEach(trigger => {
                trigger.addEventListener('click', (event) => {
                    event.preventDefault();
                    const modalId = trigger.getAttribute('data-modal-target');
                    openModal(modalId);
                });
            });

            // Add click listeners to all close buttons
            closeButtons.forEach(button => {
                button.addEventListener('click', () => {
                    closeModal();
                });
            });

            // Add click listener to close modal when clicking the overlay
            modalOverlays.forEach(overlay => {
                overlay.addEventListener('click', (event) => {
                    if (event.target === overlay) {
                        closeModal();
                    }
                });
            });
            
            // --- Quick Chat Button ---
            const quickChatBtn = document.getElementById('quickChatBtn');
            quickChatBtn.addEventListener('click', () => {
                alert('Connecting you to a Quick Chat session as a guest...');
                // In a real app, this would redirect to a guest chat room.
                // For example: window.location.href = '/chat/guest';
            });
            
            // --- Form Submission Simulation ---
            const loginForm = document.getElementById('loginForm');
            const registerForm = document.getElementById('registerForm');

            loginForm.addEventListener('submit', (event) => {
                event.preventDefault(); // Prevents page reload
                alert('Login successful! (This is a demo)');
                closeModal();
            });

            registerForm.addEventListener('submit', (event) => {
                event.preventDefault(); // Prevents page reload
                alert('Account created successfully! (This is a demo)');
                closeModal();
            });
        });
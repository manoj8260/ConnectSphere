/**
 * Chat Application Frontend — Authentication & Modal UI Handling
 * ---------------------------------------------------------------
 * This script handles:
 *  - Opening/closing modal dialogs (login, register)
 *  - Quick chat button behavior
 *  - Login form submission with Fetch API
 *  - Register form submission with Fetch API
 *  - Error handling and displaying descriptive messages
 *
 * Dependencies:
 *  - HTML should contain elements with IDs:
 *      - #loginForm (login form)
 *      - #registerForm (register form)
 *      - #loginMessage (span/div for login feedback)
 *      - #form-message (span/div for register feedback)
 *  - Modal must use attributes like [data-modal-target] and .modal-overlay
 */

document.addEventListener("DOMContentLoaded", () => {
  // ================================================================
  // 🔹 Modal Handling
  // ================================================================
  const modalTriggers = document.querySelectorAll("[data-modal-target]");
  const closeButtons = document.querySelectorAll(".close-btn");
  const modalOverlays = document.querySelectorAll(".modal-overlay");

  const openModal = (modalId) => {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add("active");
  };

  const closeModal = () => {
    document.querySelector(".modal-overlay.active")?.classList.remove("active");
  };

  modalTriggers.forEach((trigger) => {
    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      const modalId = trigger.getAttribute("data-modal-target");
      openModal(modalId);
    });
  });

  closeButtons.forEach((button) =>
    button.addEventListener("click", closeModal)
  );

  modalOverlays.forEach((overlay) => {
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) closeModal();
    });
  });

  // ================================================================
  // 🔹 Quick Chat Button
  // ================================================================
  const quickChatBtn = document.getElementById("quickChatBtn");
  if (quickChatBtn) {
    quickChatBtn.addEventListener("click", () => {
      alert("Connecting you to a Quick Chat session as a guest...");
    });
  }

  // ================================================================
  // 🔹 Login Form
  // ================================================================
  const loginForm = document.getElementById("loginForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault(); // prevent page reload

      const messageElement = document.getElementById("loginMessage");
      if (!messageElement) {
        console.error('CRITICAL: Missing #loginMessage element in DOM.');
        return;
      }
      messageElement.textContent = ""; // clear old messages

      // Gather form data
      const formData = new FormData(loginForm);
      const data = Object.fromEntries(formData.entries());

      try {
        // Send login request
        const response = await fetch(`http://127.0.0.1:5001/api/v1/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.detail || "Login failed. Please check credentials.");
        }

        console.log("✅ Login successful:", result);
        
        // ⚠️ For demo: storing in sessionStorage
        // 👉 Recommended: use HttpOnly cookie for refreshToken in production
        sessionStorage.setItem("accessToken", result.access_token);
        sessionStorage.setItem("refreshToken", result.refresh_token);

        messageElement.textContent = "Login successful! Redirecting...";
        messageElement.style.color = "green";

        // Redirect to chat page
        setTimeout(() => {
          loginForm.reset();
          closeModal();
          window.location.href = `${window.location.origin.replace(":8000", ":8006")}/chat`;
        }, 1500);
      } catch (error) {
        console.error("❌ Login failed:", error);
        messageElement.textContent = error.message;
        messageElement.style.color = "red";
      }
    });
  }

  // ================================================================
  // 🔹 Register Form
  // ================================================================
  const registerForm = document.getElementById("registerForm");

  if (registerForm) {
    const messageElement = registerForm.querySelector("#form-message");

    const showMessage = (message, type) => {
      messageElement.innerHTML = message;
      messageElement.className = `form-message ${type}`;
    };

    registerForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      messageElement.className = "form-message"; // reset style

      const formData = new FormData(event.target);
      const data = Object.fromEntries(formData.entries());

      try {
        const response = await fetch(`http://127.0.0.1:5001/api/v1/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });

        const result = await response.json();

        if (!response.ok) {
          console.error("Backend error details:", result);
          throw new Error(getErrorMessage(result));
        }

        console.log("✅ Registration successful:", result);
        showMessage(`Registration successful! Welcome, ${result.name}`, "success");

        setTimeout(() => {
          closeModal();
          registerForm.reset();
          messageElement.className = "form-message";
        }, 2000);
      } catch (error) {
        console.error("❌ Registration failed:", error);
        showMessage(`Registration failed:<br>${error.message}`, "error");
      }
    });
  }
});

/**
 * Extract descriptive messages from FastAPI error responses.
 *
 * @param {object} errorData - JSON returned by FastAPI on error
 * @returns {string} Human-readable error string (supports 422 validation errors)
 */
function getErrorMessage(errorData) {
  if (errorData.detail) {
    if (Array.isArray(errorData.detail)) {
      // Handles FastAPI validation errors (422)
      return errorData.detail.map((err) => err.msg).join("<br>");
    }
    return errorData.detail; // Handles custom exceptions
  }
  return "An unknown error occurred.";
}
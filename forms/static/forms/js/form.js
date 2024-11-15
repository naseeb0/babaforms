// forms/static/forms/js/form.js
class FormLoader {
  constructor() {
    this.formId = document.currentScript.getAttribute("data-form-id");
    this.formType = document.currentScript.getAttribute("data-form-type");
    // Add base URL for API calls
    this.apiBaseUrl = "http://146.190.251.72"; // For development
    this.loadForm();
  }

  getFormTemplate() {
    const commonClasses = {
      input: "w-full p-2 mb-4 border rounded",
      label: "block mb-2 text-gray-700",
      button: "bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600",
    };

    return `
            <form id="embedded-form" class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
                <div class="mb-4">
                    <label class="${commonClasses.label}">Name</label>
                    <input type="text" name="name" required class="${commonClasses.input}">
                </div>
                <div class="mb-4">
                    <label class="${commonClasses.label}">Email</label>
                    <input type="email" name="email" required class="${commonClasses.input}">
                </div>
                <div class="mb-4">
                    <label class="${commonClasses.label}">Phone</label>
                    <input type="tel" name="phone" required class="${commonClasses.input}">
                </div>
                <div class="mb-4">
                    <label class="${commonClasses.label}">
                        <input type="checkbox" name="is_realtor" class="mr-2">
                        Are you a realtor?
                    </label>
                </div>
                <div class="mb-4">
                    <label class="${commonClasses.label}">Message</label>
                    <textarea name="message" required class="${commonClasses.input}" rows="4"></textarea>
                </div>
                <button type="submit" class="${commonClasses.button}">Submit</button>
                <div id="form-status" class="mt-4 hidden"></div>
            </form>
        `;
  }

  showStatus(message, isError = false) {
    const statusDiv = document.getElementById("form-status");
    statusDiv.className = `mt-4 p-4 rounded ${
      isError ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
    }`;
    statusDiv.textContent = message;
    statusDiv.classList.remove("hidden");
  }

  async loadForm() {
    const container = document.createElement("div");
    container.innerHTML = this.getFormTemplate();
    document.currentScript.parentNode.insertBefore(
      container,
      document.currentScript
    );

    document
      .getElementById("embedded-form")
      .addEventListener("submit", async (e) => {
        e.preventDefault();

        // Show loading state
        const submitButton = e.target.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        submitButton.textContent = "Submitting...";
        submitButton.disabled = true;

        const formData = {
          name: e.target.name.value,
          email: e.target.email.value,
          phone: e.target.phone.value,
          is_realtor: e.target.is_realtor.checked,
          message: e.target.message.value,
        };

        try {
          const response = await fetch(
            `${this.apiBaseUrl}/api/submit/${this.formId}/`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(formData),
            }
          );

          const data = await response.json();

          if (response.ok) {
            this.showStatus(data.message || "Form submitted successfully!");
            e.target.reset();
          } else {
            this.showStatus(
              data.message || "Submission failed. Please try again.",
              true
            );
          }
        } catch (error) {
          console.error("Error:", error);
          this.showStatus(
            "Network error. Please check your connection and try again.",
            true
          );
        } finally {
          // Restore button state
          submitButton.textContent = originalButtonText;
          submitButton.disabled = false;
        }
      });
  }
}

new FormLoader();

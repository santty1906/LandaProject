(function () {
    "use strict";

    let stream = null;
    let capturedImages = {};
    let captureStep = "frontal";

    const faceModal = document.getElementById("faceModal");
    if (!faceModal) return;

    const video = document.getElementById("faceVideo");
    const canvas = document.getElementById("faceCanvas");
    const preview = document.getElementById("facePreview");
    const instruction = document.getElementById("faceInstruction");
    const captureBtn = document.getElementById("captureFaceBtn");
    const saveBtn = document.getElementById("saveFaceBtn");
    const status = document.getElementById("faceStatus");

    const enrollBtn = document.getElementById("enrollFaceBtn");
    const reEnrollBtn = document.getElementById("reEnrollFaceBtn");

    if (enrollBtn) enrollBtn.addEventListener("click", () => startEnrollment());
    if (reEnrollBtn) reEnrollBtn.addEventListener("click", () => startEnrollment());

    const bsModal = new bootstrap.Modal(faceModal);
    faceModal.addEventListener("hidden.bs.modal", stopCamera);

    function startEnrollment() {
        capturedImages = {};
        captureStep = "frontal";
        preview.innerHTML = "";
        saveBtn.classList.add("d-none");
        captureBtn.classList.remove("d-none");
        instruction.textContent = "Position your FRONTAL face in the center";
        startCamera();
        bsModal.show();
    }

    async function startCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: 320 } });
            video.srcObject = stream;
        } catch (err) {
            status.textContent = "Camera access denied. Please allow camera permissions.";
            status.className = "text-danger small";
        }
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(function (t) {
                t.stop();
            });
            stream = null;
        }
        video.srcObject = null;
    }

    function captureImage() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0);
        const dataUrl = canvas.toDataURL("image/jpeg", 0.8);

        capturedImages[captureStep] = dataUrl;

        const img = document.createElement("img");
        img.src = dataUrl;
        img.className = "rounded-2 border";
        img.style.width = "80px";
        img.style.height = "80px";
        img.style.objectFit = "cover";
        preview.appendChild(img);

        const steps = ["frontal", "left", "right"];
        const currentIdx = steps.indexOf(captureStep);
        if (currentIdx < steps.length - 1) {
            captureStep = steps[currentIdx + 1];
            instruction.textContent = "Now turn your face to the " + captureStep.toUpperCase();
            status.textContent = "Captured " + steps[currentIdx] + ". " + (steps.length - currentIdx - 1) + " more.";
            status.className = "text-success small";
        } else {
            instruction.textContent = "All angles captured!";
            captureBtn.classList.add("d-none");
            saveBtn.classList.remove("d-none");
            status.textContent = "3/3 captured. Click Save to enroll.";
            status.className = "text-success small";
        }
    }

    captureBtn.addEventListener("click", captureImage);

    saveBtn.addEventListener("click", async function () {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';
        status.textContent = "Enrolling face...";
        status.className = "text-info small";

        try {
            const resp = await fetch("/auth/../api/face/enroll", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ images: capturedImages }),
            });

            if (resp.ok) {
                status.textContent = "Face enrolled successfully!";
                status.className = "text-success fw-bold small";
                setTimeout(function () { bsModal.hide(); location.reload(); }, 1000);
            } else {
                const data = await resp.json();
                status.textContent = data.error || "Enrollment failed.";
                status.className = "text-danger small";
                saveBtn.disabled = false;
                saveBtn.innerHTML = '<i class="bi bi-check2 me-1"></i>Save';
            }
        } catch (err) {
            status.textContent = "Network error. Please try again.";
            status.className = "text-danger small";
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="bi bi-check2 me-1"></i>Save';
        }
    });

    window.LandaFace = {
        verify: async function (imageDataUrl) {
            try {
                const resp = await fetch("/auth/../api/face/verify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ image: imageDataUrl }),
                });
                return resp.ok;
            } catch {
                return false;
            }
        },
    };
})();

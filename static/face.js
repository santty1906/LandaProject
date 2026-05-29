(() => {
  const root = document.querySelector('[data-face-wizard="true"]');
  if (!root || !window.FACE_WIZARD) {
    return;
  }

  const video = document.getElementById("faceVideo");
  const captureButton = document.getElementById("faceCaptureButton");
  const stepTitle = document.getElementById("faceStepTitle");
  const stepDescription = document.getElementById("faceStepDescription");
  const stepLabel = document.getElementById("faceStepLabel");
  const statusLabel = document.getElementById("faceStatus");
  const chips = Array.from(document.querySelectorAll("#facePoseChips .chip"));

  const poses = window.FACE_WIZARD.poses || [];
  const mode = window.FACE_WIZARD.mode;
  let currentStep = 0;
  let stream = null;

  const descriptions = {
    frontal: "Mira al frente y centra el rostro dentro del círculo.",
    izquierda:
      "Gira levemente la cabeza hacia la izquierda sin salir del círculo.",
    derecha: "Gira levemente la cabeza hacia la derecha sin salir del círculo.",
  };

  const titles = {
    enroll: "Captura de enrolamiento",
    login: "Captura de verificación",
  };

  function setStep(step) {
    const pose = poses[step] || poses[poses.length - 1] || "frontal";
    currentStep = step;
    if (stepTitle) {
      stepTitle.textContent = `${titles[mode] || "Captura"} · ${pose}`;
    }
    if (stepDescription) {
      stepDescription.textContent =
        descriptions[pose] ||
        "Mantén el rostro centrado y evita movimientos bruscos.";
    }
    if (stepLabel) {
      stepLabel.textContent = `Paso ${step + 1} de ${poses.length}: ${pose}`;
    }
    chips.forEach((chip, index) => {
      chip.classList.toggle("active", index === step);
      chip.classList.toggle("done", index < step);
    });
  }

  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });
      video.srcObject = stream;
      statusLabel.textContent =
        "Cámara activa. Ajusta el rostro dentro del círculo.";
      setStep(0);
    } catch (error) {
      statusLabel.textContent =
        "No se pudo abrir la cámara. Puedes volver y usar contraseña.";
      captureButton.disabled = true;
    }
  }

  function captureFrame() {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.92));
  }

  async function sendCapture(blob, pose, finalStep) {
    const formData = new FormData();
    formData.append("mode", mode);
    formData.append("pose", pose);
    formData.append("step_index", String(currentStep));
    formData.append("final_step", finalStep ? "true" : "false");
    formData.append("frame", blob, `face-${pose}.jpg`);

    const response = await fetch(window.FACE_WIZARD.captureUrl, {
      method: "POST",
      body: formData,
    });
    return response.json();
  }

  async function handleCapture() {
    const pose = poses[currentStep] || poses[0];
    const blob = await captureFrame();
    if (!blob) {
      statusLabel.textContent = "No se pudo capturar la imagen.";
      return;
    }

    captureButton.disabled = true;
    statusLabel.textContent = "Procesando captura...";

    try {
      const result = await sendCapture(
        blob,
        pose,
        currentStep === poses.length - 1,
      );
      if (!result.ok) {
        statusLabel.textContent = result.message || "La captura fue rechazada.";
        captureButton.disabled = false;
        return;
      }

      if (result.complete) {
        statusLabel.textContent = result.message || "Proceso completado.";
        window.location.href =
          result.redirect_url || window.FACE_WIZARD.redirectUrl;
        return;
      }

      statusLabel.textContent = result.message || "Captura aceptada.";
      if (currentStep < poses.length - 1) {
        setStep(currentStep + 1);
      }
      captureButton.disabled = false;
    } catch (error) {
      statusLabel.textContent = "Ocurrió un problema al enviar la captura.";
      captureButton.disabled = false;
    }
  }

  captureButton.addEventListener("click", handleCapture);
  startCamera();
})();

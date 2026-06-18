/**
 * SecureFile — Web Crypto Engine
 * ================================================================
 * Implements a Fernet-compatible (AES-128-CBC + HMAC-SHA256) file
 * encryption and decryption engine using the browser's built-in
 * Web Crypto API. No external libraries required.
 *
 * File format written/read:
 *   [16 bytes PBKDF2 salt] + [base64url-encoded Fernet token]
 *
 * Fernet token structure:
 *   Version (1B 0x80) | Timestamp (8B BE) | IV (16B) | Ciphertext | HMAC-SHA256 (32B)
 *
 * Key derivation:
 *   raw_key = PBKDF2(password, salt, iterations=100000, hash=SHA-256, length=32B)
 *   signing_key  = raw_key[0:16]   (HMAC-SHA256)
 *   encryption_key = raw_key[16:32] (AES-128-CBC)
 * ================================================================
 */

"use strict";

document.addEventListener("DOMContentLoaded", () => {

    /* ------------------------------------------------------------------ */
    /*  Element References                                                  */
    /* ------------------------------------------------------------------ */

    const dropZone        = document.getElementById("dropZone");
    const fileInput       = document.getElementById("fileInput");
    const dropPrompt      = document.getElementById("dropPrompt");
    const fileMetadata    = document.getElementById("fileMetadata");
    const btnClearFile    = document.getElementById("btnClearFile");

    const metaIcon        = document.getElementById("metaIcon");
    const metaFilename    = document.getElementById("metaFilename");
    const metaStatus      = document.getElementById("metaStatus");
    const metaSize        = document.getElementById("metaSize");
    const metaType        = document.getElementById("metaType");

    const passwordInput   = document.getElementById("passwordInput");
    const btnTogglePwd    = document.getElementById("btnTogglePwd");
    const strengthText    = document.getElementById("strengthText");
    const strengthBar     = document.getElementById("strengthBar");

    const btnEncrypt      = document.getElementById("btnEncrypt");
    const btnDecrypt      = document.getElementById("btnDecrypt");

    const resultCard      = document.getElementById("resultCard");
    const resultTitle     = document.getElementById("resultTitle");
    const resultDesc      = document.getElementById("resultDesc");
    const btnDownload     = document.getElementById("btnDownload");
    const btnCopyName     = document.getElementById("btnCopyName");

    const errorAlert      = document.getElementById("errorAlert");
    const errorMsg        = document.getElementById("errorMsg");
    const btnCloseError   = document.getElementById("btnCloseError");

    const activityList    = document.getElementById("activityList");
    const processingOverlay = document.getElementById("processingOverlay");

    /* ------------------------------------------------------------------ */
    /*  Application State                                                   */
    /* ------------------------------------------------------------------ */

    let selectedFile          = null;
    let isProcessing          = false;
    let lastGeneratedFilename = "";
    let lastObjectUrl         = null;

    /* ------------------------------------------------------------------ */
    /*  1. Drag-and-Drop & File Selection                                   */
    /* ------------------------------------------------------------------ */

    // Prevent browser default open-file on drop
    ["dragenter", "dragover", "dragleave", "drop"].forEach(evt => {
        dropZone.addEventListener(evt,   stopEvent, false);
        document.body.addEventListener(evt, stopEvent, false);
    });

    function stopEvent(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Visual highlight on drag-enter / drag-over
    ["dragenter", "dragover"].forEach(evt =>
        dropZone.addEventListener(evt, () => dropZone.classList.add("dragover"))
    );
    ["dragleave", "drop"].forEach(evt =>
        dropZone.addEventListener(evt, () => dropZone.classList.remove("dragover"))
    );

    // Drop handler
    dropZone.addEventListener("drop", e => {
        const files = e.dataTransfer && e.dataTransfer.files;
        if (files && files.length > 0) pickFile(files[0]);
    });

    // Click-to-browse handler
    fileInput.addEventListener("change", e => {
        if (e.target.files && e.target.files.length > 0) pickFile(e.target.files[0]);
    });

    function pickFile(file) {
        if (file.size > 50 * 1024 * 1024) {
            showError("File too large. The web tool supports files up to 50 MB.");
            return;
        }
        selectedFile = file;
        hideError();
        hideResult();
        renderFileMeta(file);
        validateInputs();
    }

    function renderFileMeta(file) {
        const isEnc = file.name.toLowerCase().endsWith(".enc");

        metaFilename.textContent = file.name;
        metaFilename.title       = file.name;
        metaSize.textContent     = formatBytes(file.size);
        metaType.textContent     = getExtension(file.name);

        if (isEnc) {
            metaIcon.textContent   = "🔒";
            metaStatus.textContent = "🔒 Encrypted File";
            metaStatus.className   = "meta-badge encrypted";
        } else {
            metaIcon.textContent   = "📄";
            metaStatus.textContent = "📄 Ready to Encrypt";
            metaStatus.className   = "meta-badge raw";
        }

        dropPrompt.style.display   = "none";
        fileMetadata.style.display = "block";
    }

    btnClearFile.addEventListener("click", e => {
        e.stopPropagation();
        clearFile();
    });

    function clearFile() {
        selectedFile    = null;
        fileInput.value = "";
        fileMetadata.style.display = "none";
        dropPrompt.style.display   = "flex";
        validateInputs();
        hideResult();
        hideError();
    }

    /* ------------------------------------------------------------------ */
    /*  2. Password Handling                                                */
    /* ------------------------------------------------------------------ */

    passwordInput.addEventListener("input", () => {
        updateStrengthUI(passwordInput.value);
        validateInputs();
    });

    btnTogglePwd.addEventListener("click", () => {
        const hidden = passwordInput.type === "password";
        passwordInput.type      = hidden ? "text" : "password";
        btnTogglePwd.textContent = hidden ? "🙈" : "👁️";
        btnTogglePwd.title       = hidden ? "Hide Password" : "Show Password";
    });

    function updateStrengthUI(pwd) {
        const len = pwd.length;
        strengthBar.className = "strength-bar";

        if (len === 0) {
            strengthText.textContent = "";
            strengthText.style.color = "inherit";
        } else if (len < 6) {
            strengthBar.classList.add("strength-weak");
            strengthText.textContent = "Weak";
            strengthText.style.color = "var(--error-color)";
        } else if (len < 10) {
            strengthBar.classList.add("strength-medium");
            strengthText.textContent = "Medium";
            strengthText.style.color = "#fbbf24";
        } else {
            strengthBar.classList.add("strength-strong");
            strengthText.textContent = "Strong";
            strengthText.style.color = "var(--success-color)";
        }
    }

    function validateInputs() {
        const ready = selectedFile !== null && passwordInput.value.length > 0;
        btnEncrypt.disabled = !ready;
        btnDecrypt.disabled = !ready;
    }

    /* ------------------------------------------------------------------ */
    /*  3. Cryptographic Engine (Fernet-compatible via Web Crypto API)     */
    /* ------------------------------------------------------------------ */

    /** Convert Uint8Array → base64url string (no padding) */
    function toBase64url(bytes) {
        let bin = "";
        for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
        return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    }

    /** Convert base64url string → Uint8Array */
    function fromBase64url(str) {
        let b64 = str.replace(/-/g, "+").replace(/_/g, "/");
        while (b64.length % 4) b64 += "=";
        const bin   = atob(b64);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return bytes;
    }

    /**
     * Derives [signingKey, encryptionKey] from password + salt using PBKDF2.
     * Returns two 16-byte CryptoKey objects.
     */
    async function deriveKeys(password, salt) {
        const enc          = new TextEncoder();
        const baseKey      = await crypto.subtle.importKey(
            "raw", enc.encode(password), "PBKDF2", false, ["deriveBits"]
        );
        const rawBits      = await crypto.subtle.deriveBits(
            { name: "PBKDF2", salt, iterations: 100000, hash: "SHA-256" },
            baseKey, 256
        );
        const raw          = new Uint8Array(rawBits);
        const signingBytes = raw.slice(0, 16);
        const encBytes     = raw.slice(16, 32);

        const signingKey = await crypto.subtle.importKey(
            "raw", signingBytes, { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]
        );
        const encKey = await crypto.subtle.importKey(
            "raw", encBytes, { name: "AES-CBC" }, false, ["encrypt", "decrypt"]
        );
        return { signingKey, encKey };
    }

    /**
     * Encrypt plaintext ArrayBuffer with password + given salt.
     * Returns a Uint8Array = [salt (16B)] + [base64url Fernet token (ASCII)]
     */
    async function encryptBuffer(plainBuffer, password, salt) {
        const { signingKey, encKey } = await deriveKeys(password, salt);

        // IV = 16 random bytes
        const iv = crypto.getRandomValues(new Uint8Array(16));

        // Big-endian 64-bit timestamp (seconds since epoch)
        const ts          = BigInt(Math.floor(Date.now() / 1000));
        const tsBytes     = new Uint8Array(8);
        const tsView      = new DataView(tsBytes.buffer);
        tsView.setBigUint64(0, ts, false);

        // AES-128-CBC encrypt (Web Crypto adds PKCS7 padding automatically)
        const cipherBuf  = await crypto.subtle.encrypt({ name: "AES-CBC", iv }, encKey, plainBuffer);
        const cipher     = new Uint8Array(cipherBuf);

        // Build Fernet payload: version(1) | ts(8) | iv(16) | ciphertext
        const payload    = new Uint8Array(1 + 8 + 16 + cipher.length);
        payload[0]       = 0x80;
        payload.set(tsBytes, 1);
        payload.set(iv, 9);
        payload.set(cipher, 25);

        // HMAC-SHA256 signature over payload
        const sigBuf     = await crypto.subtle.sign("HMAC", signingKey, payload);
        const sig        = new Uint8Array(sigBuf);

        // Full token = payload | sig(32)
        const token      = new Uint8Array(payload.length + sig.length);
        token.set(payload, 0);
        token.set(sig, payload.length);

        // Encode token as base64url ASCII string
        const tokenAscii = new TextEncoder().encode(toBase64url(token));

        // Final file = salt(16) | tokenAscii
        const out        = new Uint8Array(16 + tokenAscii.length);
        out.set(salt, 0);
        out.set(tokenAscii, 16);
        return out;
    }

    /**
     * Decrypt a file ArrayBuffer that was produced by encryptBuffer (or by
     * the Python SecureFile desktop app). Returns decrypted ArrayBuffer.
     * Throws descriptive Error on any failure.
     */
    async function decryptBuffer(fileBuffer, password) {
        const bytes = new Uint8Array(fileBuffer);

        if (bytes.length < 17) throw new Error("Invalid file — too small to contain a valid encrypted token.");

        const salt           = bytes.slice(0, 16);
        const tokenAscii     = new TextDecoder("utf-8").decode(bytes.slice(16)).trim();

        let tokenBytes;
        try {
            tokenBytes = fromBase64url(tokenAscii);
        } catch {
            throw new Error("Corrupted file — cannot parse base64url token.");
        }

        // Minimum token length: 1 + 8 + 16 + 16 + 32 = 73 bytes (16-byte min ciphertext block)
        if (tokenBytes.length < 73) {
            throw new Error("Invalid file structure — token is too short.");
        }

        const version = tokenBytes[0];
        if (version !== 0x80) throw new Error(`Unsupported token version: 0x${version.toString(16)}`);

        // Parse token fields
        const iv         = tokenBytes.slice(9, 25);
        const sig        = tokenBytes.slice(tokenBytes.length - 32);
        const payload    = tokenBytes.slice(0, tokenBytes.length - 32);
        const ciphertext = tokenBytes.slice(25, tokenBytes.length - 32);

        const { signingKey, encKey } = await deriveKeys(password, salt);

        // Verify HMAC-SHA256 signature BEFORE attempting decryption
        const valid = await crypto.subtle.verify("HMAC", signingKey, sig, payload);
        if (!valid) throw new Error("Incorrect password or tampered file. Decryption failed.");

        // AES-128-CBC decrypt
        let decrypted;
        try {
            decrypted = await crypto.subtle.decrypt({ name: "AES-CBC", iv }, encKey, ciphertext);
        } catch {
            throw new Error("Incorrect password or corrupted ciphertext. Decryption failed.");
        }

        return decrypted;
    }

    /* ------------------------------------------------------------------ */
    /*  4. Encrypt / Decrypt Button Actions                                 */
    /* ------------------------------------------------------------------ */

    btnEncrypt.addEventListener("click", async () => {
        if (!selectedFile || isProcessing) return;

        const password = passwordInput.value;
        if (!password) { showError("Please enter a password first."); return; }

        setProcessing(true);
        hideError();
        hideResult();

        try {
            const plainBuffer = await readFileAsBuffer(selectedFile);
            const salt        = crypto.getRandomValues(new Uint8Array(16));

            // Yield to UI so spinner renders
            await tick();

            const encBytes    = await encryptBuffer(plainBuffer, password, salt);
            const outName     = selectedFile.name + ".enc";
            const blob        = new Blob([encBytes], { type: "application/octet-stream" });
            const url         = createObjectUrl(blob);

            showResult(url, outName);
            logActivity(outName, "Encrypt");
            triggerDownload(url, outName);

        } catch (err) {
            showError("Encryption failed: " + err.message);
        } finally {
            setProcessing(false);
        }
    });

    btnDecrypt.addEventListener("click", async () => {
        if (!selectedFile || isProcessing) return;

        const password = passwordInput.value;
        if (!password) { showError("Please enter a password first."); return; }

        if (!selectedFile.name.toLowerCase().endsWith(".enc")) {
            showError("The selected file does not appear to be encrypted (.enc extension required for decryption).");
            return;
        }

        setProcessing(true);
        hideError();
        hideResult();

        try {
            const encBuffer = await readFileAsBuffer(selectedFile);

            // Yield to UI so spinner renders
            await tick();

            const decBuffer = await decryptBuffer(encBuffer, password);

            // Restore original filename: strip ".enc" suffix
            const rawName   = selectedFile.name.slice(0, -4) || "decrypted_file";
            const blob      = new Blob([decBuffer], { type: "application/octet-stream" });
            const url       = createObjectUrl(blob);

            showResult(url, rawName);
            logActivity(rawName, "Decrypt");
            triggerDownload(url, rawName);

        } catch (err) {
            showError(err.message);
        } finally {
            setProcessing(false);
        }
    });

    /* ------------------------------------------------------------------ */
    /*  5. UI State Helpers                                                 */
    /* ------------------------------------------------------------------ */

    function setProcessing(active) {
        isProcessing = active;
        processingOverlay.classList.toggle("active", active);
        btnEncrypt.disabled = active;
        btnDecrypt.disabled = active;
    }

    function showResult(url, filename) {
        lastGeneratedFilename = filename;

        // Revoke old object URL to free memory
        if (lastObjectUrl) URL.revokeObjectURL(lastObjectUrl);
        lastObjectUrl = url;

        resultTitle.textContent  = "🎉 File Processed Successfully!";
        resultDesc.innerHTML     =
            `Output: <strong style="font-family:var(--font-mono)">${escapeHtml(filename)}</strong><br>
             Download should start automatically — use the button below if it did not.`;
        btnDownload.href         = url;
        btnDownload.download     = filename;
        resultCard.style.display = "block";
    }

    function hideResult() {
        resultCard.style.display = "none";
    }

    function showError(message) {
        errorMsg.textContent = message;
        errorAlert.classList.add("visible");
        errorAlert.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function hideError() {
        errorAlert.classList.remove("visible");
    }

    btnCloseError.addEventListener("click", hideError);

    btnCopyName.addEventListener("click", () => {
        if (!lastGeneratedFilename) return;
        navigator.clipboard.writeText(lastGeneratedFilename)
            .then(() => {
                const orig = btnCopyName.innerHTML;
                btnCopyName.innerHTML = "✅ Copied!";
                setTimeout(() => { btnCopyName.innerHTML = orig; }, 1800);
            })
            .catch(() => showError("Could not access clipboard. Please copy manually: " + lastGeneratedFilename));
    });

    /* ------------------------------------------------------------------ */
    /*  6. Recent Activity Log (persisted in localStorage)                  */
    /* ------------------------------------------------------------------ */

    const STORAGE_KEY = "securefile_activity_log";

    function loadActivityLog() {
        try {
            const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
            renderLog(data);
        } catch {
            renderLog([]);
        }
    }

    function logActivity(filename, action) {
        let logs = [];
        try { logs = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]"); } catch {}

        const now = new Date();
        const ts  = now.toTimeString().slice(0, 8); // "HH:MM:SS"

        logs.unshift({ ts, filename, action });
        logs = logs.slice(0, 5); // keep last 5 entries
        localStorage.setItem(STORAGE_KEY, JSON.stringify(logs));
        renderLog(logs);
    }

    function renderLog(logs) {
        if (!logs || logs.length === 0) {
            activityList.innerHTML = `<div class="activity-empty">No recent activity. Encrypt or decrypt a file to log history.</div>`;
            return;
        }

        activityList.innerHTML = "";
        logs.forEach(entry => {
            const item      = document.createElement("div");
            item.className  = "activity-item";
            const badgeCls  = entry.action.toLowerCase() === "encrypt" ? "encrypt" : "decrypt";
            item.innerHTML  = `
                <div class="activity-meta-left">
                    <span class="act-time">[${escapeHtml(entry.ts)}]</span>
                    <span class="act-file" title="${escapeHtml(entry.filename)}">${escapeHtml(entry.filename)}</span>
                </div>
                <span class="act-badge ${badgeCls}">${escapeHtml(entry.action)}</span>
            `;
            activityList.appendChild(item);
        });
    }

    /* ------------------------------------------------------------------ */
    /*  7. Utility Functions                                                */
    /* ------------------------------------------------------------------ */

    /** Read a File object as ArrayBuffer (Promise wrapper). */
    function readFileAsBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader      = new FileReader();
            reader.onload     = () => resolve(reader.result);
            reader.onerror    = () => reject(new Error("Failed to read the selected file."));
            reader.readAsArrayBuffer(file);
        });
    }

    /** Trigger a browser file download without navigating away. */
    function triggerDownload(url, filename) {
        const a      = document.createElement("a");
        a.href       = url;
        a.download   = filename;
        a.style.display = "none";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    /** Create an object URL and track it. */
    function createObjectUrl(blob) {
        return URL.createObjectURL(blob);
    }

    /** Format bytes into human-readable string. */
    function formatBytes(bytes) {
        if (bytes === 0) return "0 Bytes";
        const k     = 1024;
        const units = ["Bytes", "KB", "MB", "GB"];
        const i     = Math.min(Math.floor(Math.log(bytes) / Math.log(k)), units.length - 1);
        return `${(bytes / Math.pow(k, i)).toFixed(i > 0 ? 2 : 0)} ${units[i]}`;
    }

    /** Return uppercase file extension or "NONE". */
    function getExtension(filename) {
        const idx = filename.lastIndexOf(".");
        if (idx < 0 || idx === filename.length - 1) return "NONE";
        return filename.slice(idx + 1).toUpperCase();
    }

    /** Escape HTML characters to prevent XSS in innerHTML. */
    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    /** Yield to the event loop (allows the browser to repaint). */
    function tick() {
        return new Promise(r => setTimeout(r, 30));
    }

    /* ------------------------------------------------------------------ */
    /*  8. Init                                                             */
    /* ------------------------------------------------------------------ */

    loadActivityLog();
    validateInputs();

}); // end DOMContentLoaded
